__version__ = "1.0.0"

import sys
import os
import re

PYTHON_TEMPLATE = """# {0}

import argparse

def main():
    parser = argparse.ArgumentParser(description='',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

{1}
    args = parser.parse_args()

{2}

if __name__ == "__main__":
    main()
"""

class ArgType(object):
    """
    Enumerates all argument types that will be recognized
    """
    INT = "int"
    FLOAT = "float"
    FILE = "argparse.FileType()"
    STRING = "str"


class CmdlineOpt(object):
    """
    Represents a single option / flag / positional argument parsed from command line arguments
    """

    # Return values for add_arg
    SUCCESS = 0
    SUCCESS_AND_FULL = 1
    FAILURE = 2

    nonalpha_rgx = re.compile("[^0-9a-zA-Z\-\_]")

    def __init__(self):
        self.value = None
        self.opt = None
        self.longopt = None
        self.type = None
        self.var_name = None

    def finalize(self):
        """
        Called for final post-processing after all required data for a single
        CmdlineOpt instance has been collected
        """
        if self.is_positional():
            varname = self.value
        else:
            if self.longopt is not None:
                varname = self.longopt
            elif self.opt is not None:
                varname = self.opt
            else:
                raise RuntimeError(f"Invalid attribute values for {self.__class__.__name__}")

        self.var_name = varname.lstrip('-').replace('-', '_')

        if self.value is None:
            return
        try:
            intval = int(self.value)
        except ValueError:
            pass
        else:
            self.type = ArgType.INT

        if self.type is None:
            try:
                fltval = float(self.value)
            except ValueError:
                pass
            else:
                self.type = ArgType.FLOAT

        if self.type is None:
            if os.path.isfile(self.value):
                self.type = ArgType.FILE
            else:
                self.type = ArgType.STRING

    def add_arg(self, arg):
        """
        Process a single argument command-line argument

        :param str arg: the command-line argument to process
        :return: 0 if success and room for more, 1 if success but no more room, 2 if no room
        """
        cleaned_arg = self.nonalpha_rgx.sub('-', arg)

        if arg.startswith('--'):
            if self.longopt is None:
                self.longopt = cleaned_arg
            else:
                return self.FAILURE

        elif arg.startswith('-'):
            if self.opt is None:
                self.opt = cleaned_arg
            else:
                return self.FAILURE
        else:
            if self.value is None:
                if (self.opt) or (self.longopt):
                    self.value = arg
                else:
                    self.value = arg.replace('-', '_')

            return self.SUCCESS_AND_FULL

        return self.SUCCESS

    def opttext(self):
        ret = ""
        if self.opt is not None:
            ret += f"'{self.opt}', "
        if self.longopt is not None:
            ret += f"'{self.longopt}', "

        return ret

    def generate_code(self):
        """
        Generate the 'parser.add_argument(...)' line for this option

        :return: Line of python code to add this option to the arg parser
        :rtype: str
        """
        if self.is_flag():
            funcargs = self.opttext() + "action='store_true'"

        elif self.is_option():
            if self.type in [ArgType.FILE, ArgType.STRING]:
                value = f"'{self.value}'"
            else:
                value = self.value

            funcargs = self.opttext() + f"default={value}"
            if self.type is not ArgType.STRING:
                funcargs += f", type={self.type}"

        elif self.is_positional():
            funcargs = f"'{self.value}'"
        else:
            raise RuntimeError('Invalid options provided')

        if self.type is not None:
            if self.type == ArgType.INT:
                helptext = "an int value"
            elif self.type == ArgType.FLOAT:
                helptext = "a float value"
            elif self.type == ArgType.FILE:
                helptext = "a filename"
            elif self.type == ArgType.STRING:
                helptext = "a string"
            else:
                raise RuntimeError('Invalid type setting')

        elif self.is_flag():
            helptext = f"{self.var_name} flag"

        funcargs += f", help='{helptext}'"

        return f"parser.add_argument({funcargs})"

    def is_empty(self):
        """
        Returns true if nothing has been set yet
        """
        return (self.value is None) and (self.opt is None) and (self.longopt is None)

    def is_flag(self):
        """
        Returns true if this is an option with no argument (a flag)
        """
        return ((self.opt is not None) or (self.longopt is not None)) and self.value is None

    def is_option(self):
        """
        Returns true if this is an option with an argument
        """
        return ((self.opt is not None) or (self.longopt is not None)) and self.value is not None

    def is_positional(self):
        """
        Returns true if this is a positional argument
        """
        return (self.opt is None) and (self.longopt is None) and (self.value is not None)

    def __str__(self):
        return f"{self.__class__.__name__}({self.opt}, {self.longopt}, {self.value})"

    def __repr__(self):
        return self.__str__()


def process_args(argv=sys.argv):
    """
    Process all command line arguments and return a list of CmdlineOpt instances

    :return: List of CmdlineOpt instances
    """
    ret = []
    curr = CmdlineOpt()

    for arg in argv[1:]:
        status = curr.add_arg(arg)
        if status != CmdlineOpt.SUCCESS:
            curr.finalize()
            ret.append(curr)
            curr = CmdlineOpt()

            if status == CmdlineOpt.FAILURE:
                curr.add_arg(arg)

    if not curr.is_empty():
        curr.finalize()
        ret.append(curr)

    # Check for duplicate attr names
    seen_attr_names = {}
    for o in ret:
        if o.var_name in seen_attr_names:
            raise ValueError(f"An option named '{o.var_name}' was used more than once")

        seen_attr_names[o.var_name] = None

    return ret


def generate_python_code(argv=sys.argv):
    """
    Process all command line arguments and return the text of a python program
    which handles the described command-line options

    :param list processed_args: List of CmdlineOpt instances

    :return: text of the corresponding python program
    :rtype: str
    """
    processed_args = process_args(argv)
    optlines = "    " + "\n    ".join([o.generate_code() for o in processed_args])
    printlines = "    " + "\n    ".join([f"print(args.{o.var_name})" for o in processed_args])
    return PYTHON_TEMPLATE.format(' '.join(argv[1:]), optlines, printlines)
