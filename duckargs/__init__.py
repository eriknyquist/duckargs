__version__ = "1.3.0"

import sys
import os
import re

PYTHON_TEMPLATE = """{0}import argparse

def main():
    parser = argparse.ArgumentParser(description='A command-line program generated by duckargs',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

{1}
    args = parser.parse_args(){2}

if __name__ == "__main__":
    main()
"""

C_TEMPLATE = """{0}#include <stdlib.h>
#include <stdio.h>
#include <getopt.h>

{1}
int parse_args(int argc, char *argv[])
{{
{2}
}}

int main(int argc, char *argv[])
{{
    int ret = parse_args(argc, argv);
    return ret;
}}
"""

class ArgType(object):
    """
    Enumerates all argument types that will be recognized
    """
    INT = "int"
    FLOAT = "float"
    FILE = "argparse.FileType()"
    STRING = "str"


def _is_int(arg):
    ret = True

    try:
        intval = int(arg)
    except ValueError:
        if ((len(arg) >= 3) and (arg[:2].lower() == "0x")) or \
           ((len(arg) >= 4) and (arg[:3].lower() == "-0x")):
            try:
                intval = int(arg, 16)
            except ValueError:
                ret = False
        else:
            ret = False

    return ret

class CmdlineOpt(object):
    """
    Represents a single option / flag / positional argument parsed from command line arguments
    """

    positional_count = 0

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

        if _is_int(self.value):
            self.type = ArgType.INT

        if self.type is None:
            try:
                fltval = float(self.value)
            except ValueError:
                pass
            else:
                self.type = ArgType.FLOAT

        if self.type is None:
            if ('FILE' == self.value) or os.path.isfile(self.value):
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

        is_int = _is_int(arg)

        if arg.startswith('--'):
            if self.opt is None:
                raise ValueError(f"long option ({arg}) is not allowed without short option")

            if self.longopt is None:
                self.longopt = cleaned_arg
            else:
                return self.FAILURE

        elif arg.startswith('-') and not is_int:
            if len(arg) > 2:
                raise ValueError(f"short option ({arg}) must have exactly one character after the dash (-)")

            if self.opt is None:
                self.opt = cleaned_arg
            else:
                return self.FAILURE
        else:
            if self.value is None:
                if (self.opt) or (self.longopt) or is_int:
                    self.value = arg
                else:
                    self.value = arg.replace('-', '_')

            return self.SUCCESS_AND_FULL

        return self.SUCCESS

    def opttext(self):
        ret = []
        if self.opt is not None:
            ret.append(f"'{self.opt}'")
        if self.longopt is not None:
            ret.append(f"'{self.longopt}'")

        return ', '.join(ret)

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

def _generate_python_code_line(opt):
    """
    Generate the 'parser.add_argument(...)' line for an option

    :return: Line of python code to add this option to the arg parser
    :rtype: str
    """
    if opt.is_flag():
        funcargs = opt.opttext() + ", action='store_true'"

    elif opt.is_option():
        funcargs = opt.opttext()
        if opt.type == ArgType.STRING:
            # Check if string argument has comma-separated choices
            choices = opt.value.split(',')
            if len(choices) > 1:
                funcargs += f", choices={choices}"
                value = f"'{choices[0]}'"
            else:
                value = f"'{opt.value}'"

        elif opt.type == ArgType.FILE:
            value = f"'{opt.value}'"
        else:
            value = opt.value

        default_str = "None" if opt.type is ArgType.FILE else str(value)
        funcargs += f", default={default_str}"

        if opt.type is not ArgType.STRING:
            funcargs += f", type={opt.type}"

    elif opt.is_positional():
        if opt.value.isidentifier():
            funcargs = f"'{opt.value}'"
        else:
            varname = f"positional_arg{CmdlineOpt.positional_count}"
            funcargs = f"'{varname}'"
            opt.var_name = varname
            CmdlineOpt.positional_count += 1

        if opt.type is not ArgType.STRING:
            funcargs += f", type={opt.type}"
    else:
        raise RuntimeError('Invalid options provided')

    if opt.type is not None:
        if opt.type == ArgType.INT:
            helptext = "an int value"
        elif opt.type == ArgType.FLOAT:
            helptext = "a float value"
        elif opt.type == ArgType.FILE:
            helptext = "a filename"
        elif opt.type == ArgType.STRING:
            helptext = "a string"
        else:
            raise RuntimeError('Invalid type setting')

    elif opt.is_flag():
        helptext = f"{opt.var_name} flag"

    funcargs += f", help='{helptext}'"

    return f"parser.add_argument({funcargs})"


def generate_python_code(argv=sys.argv):
    """
    Process all command line arguments and return the text of a python program
    which handles the described command-line options

    :param list processed_args: List of CmdlineOpt instances

    :return: text of the corresponding python program
    :rtype: str
    """
    processed_args = process_args(argv)
    optlines = "    " + "\n    ".join([_generate_python_code_line(o) for o in processed_args])

    printlines = ""
    env_print = os.environ.get('DUCKARGS_PRINT', 1)
    try:
        env_print_int = int(env_print)
    except ValueError:
        raise RuntimeError("DUCKARGS_PRINT must be an integer")

    if env_print_int > 0:
        printlines += "\n\n    " + "\n    ".join([f"print(args.{o.var_name})" for o in processed_args])

    comment = ""
    env_comment = os.environ.get("DUCKARGS_COMMENT", 1)
    try:
        env_comment_int = int(env_comment)
    except ValueError:
        raise RuntimeError("DUCKARGS_COMMENT must be an integer")

    if env_comment_int > 0:
        comment = (f"# Generated by duckargs, invoked with the following arguments:\n# " +
                   ' '.join(argv[1:]) + "\n\n")

    CmdlineOpt.positional_count = 0

    return PYTHON_TEMPLATE.format(comment, optlines, printlines)

def _generate_c_getopt_code(processed_args, getopt_string, has_longopts):
    positionals = []
    ret = "    int ch;\n\n"

    if has_longopts:
        ret += f"    while ((ch = getopt_long(argc, argv, \"{getopt_string}\", long_options, NULL)) != -1)\n"
    else:
        ret += f"    while ((ch = getopt(argc, argv, \"{getopt_string}\")) != -1)\n"

    ret += "    {\n"
    ret += "        switch (ch)\n"
    ret += "        {\n"

    for arg in processed_args:
        if arg.is_positional():
            positionals.append(arg)
            continue

        ret += f"            case '{arg.opt[1]}':\n"
        ret += f"            {{\n"

        ret += f"                 break;\n"
        ret += f"            }}\n"

    ret += f"        }}\n"
    ret += f"    }}"

    return ret

def generate_c_code(argv=sys.argv):
    """
    Process all command line arguments and return the text of a C program
    which handles the described command-line options

    :param list processed_args: List of CmdlineOpt instances

    :return: text of the corresponding C program
    :rtype: str
    """
    processed_args = process_args(argv)

    long_opts = []
    has_flags = False

    decls = ""
    getopt_string = ""

    for arg in processed_args:
        if arg.is_positional():
            continue

        typename = arg.type
        varname = arg.var_name
        value = arg.value

        if arg.is_flag():
            typename = "bool"
            value = "false"
            has_flags = True

        elif arg.type in [ArgType.STRING, ArgType.FILE]:
            typename = "char"
            varname = "*" + varname

            if arg.type == ArgType.FILE:
                if arg.value == "FILE":
                    value = "NULL"

        decls += f"static {typename} {varname} = {value};\n"

        if arg.opt:
            getopt_string += arg.opt[1]
            if not arg.is_flag():
                getopt_string += ":"

        if arg.longopt is not None:
            longopt = arg.longopt.lstrip('-')
            opt = arg.opt.lstrip('-')
            argtype = "no_argument" if arg.is_flag() else "required_argument"
            long_opts.append(f"{{\"{longopt}\", {argtype}, NULL, '{opt}'}},")

    if long_opts:
        decls += "\nstatic struct option long_options[] =\n{\n"
        decls += "\n".join(["    " + opt for opt in long_opts])
        decls += "\n    {NULL, 0, NULL, 0}\n};\n"

    comment_header = ""

    if has_flags:
        comment_header += "#include <stdbool.h>\n"

    parsing_code = _generate_c_getopt_code(processed_args, getopt_string, len(long_opts) > 0)

    return C_TEMPLATE.format(comment_header, decls, parsing_code)
