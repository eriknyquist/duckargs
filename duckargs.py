import sys
import os


class ArgType(object):
    """
    Enumerates all argument types that will be recognized
    """
    INT = "int"
    FLOAT = "float"
    FILE = "argparse.FileType('w')"
    STRING = "str"


class CmdlineOpt(object):
    """
    Represents a single option / flag / positional argument parsed from command line arguments
    """
    def __init__(self):
        self.value = None
        self.opt = None
        self.longopt = None
        self.type = None
        self.default = None

    def _finalize(self):
        try:
            intval = int(self.value)
        except ValueError:
            pass
        else:
            self.default = intval
            self.type = ArgType.INT
        
        if self.type is None:
            try:
                fltval = float(self.value)
            except ValueError:
                pass
            else:
                self.default = floatval
                self.type = ArgType.FLOAT

        if self.type is None:
            if os.path.isfile(self.value):
                self.default = self.value
                self.type = ArgType.FILE
            else:
                self.default = self.value
                self.type = ArgType.STRING

        return True

    def add_arg(self, arg):
        if arg.startswith('--'):
            if self.longopt is None:
                self.longopt = arg
            else:
                return self._finalize()

        elif arg.startswith('-'):
            if self.opt is None:
                self.opt = arg
            else:
                return self._finalize()
        else:
            if self.value is None:
                self.value = arg
            else:
                return self._finalize()

        return False

    def opttext(self):
        ret = ""
        if self.opt is not None:
            ret += f"'{self.opt}', "
        if self.longopt is not None:
            ret += f"'{self.longopt}', "

        return ret

    def generate_code(self):
        if self.is_flag():
            sig = self.opttext() + "action='store_true', help='',"
        elif self.is_option():
            sig = self.opttext() + f", help='',"

    def is_empty(self):
        return (self.value is None) and (self.opt is None) and (self.longopt is None)

    def is_flag(self):
        return ((self.opt is not None) or (self.longopt is not None)) and self.value is None

    def is_option(self):
        return ((self.opt is not None) or (self.longopt is not None)) and self.value is not None

    def is_positional(self):
        return (self.opt is None) and (self.longopt is None) and (self.value is not None)

    def __str__(self):
        return f"{self.__class__.__name__}({self.opt}, {self.longopt}, {self.value})"

    def __repr__(self):
        return self.__str__()


def process_args():
    ret = []
    curr = CmdlineOpt()

    for arg in sys.argv[1:]:
        failed = curr.add_arg(arg)
        if failed:
            ret.append(curr)
            curr = CmdlineOpt()
            curr.add_arg(arg)

    if not curr.is_empty():
        ret.append(curr)

    return ret

def main():
    print(process_args())

if __name__ == "__main__":
    main()
