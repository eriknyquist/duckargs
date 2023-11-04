__version__ = "1.5.0"

import sys
import os
import re
from keyword import iskeyword

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

{1}
void print_usage(void)
{{
{2}
}}

int parse_args(int argc, char *argv[])
{{
{3}
}}

int main(int argc, char *argv[])
{{
    if (argc < 2)
    {{
        print_usage();
        return -1;
    }}

    int ret = parse_args(argc, argv);
    if (0 != ret)
    {{
        return ret;
    }}

{4}    return 0;
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
        self.desc = None

    def finalize(self):
        """
        Called for final post-processing after all required data for a single
        CmdlineOpt instance has been collected
        """
        if self.is_positional():
            if self.value.isidentifier():
                self.var_name = self.value
            else:
                varname = f"positional_arg{CmdlineOpt.positional_count}"
                self.var_name = varname
                CmdlineOpt.positional_count += 1
        else:
            if self.longopt is not None:
                varname = self.longopt
            elif self.opt is not None:
                varname = self.opt
            else:
                raise RuntimeError(f"Invalid attribute values for {self.__class__.__name__}")

            self.var_name = varname.lstrip('-').replace('-', '_')

        self.desc = self.var_name

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


def process_args(reserved_str_check, argv=sys.argv):
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
    seen_opt_names = {}
    seen_longopt_names = {}

    for o in ret:
        if o.var_name in seen_attr_names:
            raise ValueError(f"Option '{o.var_name}' was defined more than once")
        else:
            seen_attr_names[o.var_name] = None

        if o.opt is not None:
            if o.opt in seen_opt_names:
                raise ValueError(f"Short option '{o.opt}' was defined more than once")
            else:
                seen_opt_names[o.opt] = None

        if o.longopt is not None:
            if o.longopt in seen_longopt_names:
                raise ValueError(f"Long option '{o.longopt}' was defined more than once")
            else:
                seen_longopt_names[o.opt] = None

        if reserved_str_check(o.var_name):
            # If var_name is a reserved word for generated language, append 'val'.
            # So if you pass '-i --int', for example, the var name will be 'intval'
            o.var_name += "val"

    return ret

def _is_python_reserved_str(var_name):
    if iskeyword(var_name):
        return True

    return var_name in ['int', 'float', 'bool', 'dict', 'list', 'tuple']

def _is_c_reserved_str(var_name):
    return var_name in [
        'bool', '_Bool', 'char', 'unsigned', 'short', 'int', 'long', 'size_t', 'ssize_t',
        'time_t', 'float', 'double', 'long', 'wchar_t', 'void', 'int8_t', 'uint8_t',
        'int16_t', 'uint16_t', 'int32_t', 'uint32_t', 'int64_t', 'uint64_t', 'int128_t',
        'uint128_t', 'static', 'void', 'auto', 'restrict', 'register', 'return', 'switch',
        'union', 'extern', 'enum', 'if', 'else', 'for', 'while', 'do', 'break', 'signed',
        'sizeof', 'typedef', 'struct', 'case', 'default', 'volatile', 'goto', 'continue',
        'const'
    ]

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
            funcargs = f"'{opt.var_name}'"

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
        helptext = f"{opt.desc} flag"

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
    processed_args = process_args(_is_python_reserved_str, argv)
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

def _generate_c_opt_lines(arg, desc=None, optarg='optarg'):
    ret = []

    if desc is None:
        desc = f"Option '{arg.opt}'"

    if arg.is_flag():
        ret.append(f"{arg.var_name} = true;")

    elif ArgType.FLOAT == arg.type:
        ret.append(f"{arg.var_name} = strtof({optarg}, &endptr);")
        ret.append(f"if (endptr == {optarg})")
        ret.append(f"{{")
        ret.append(f"    printf(\"{desc} requires a floating-point argument\\n\");")
        ret.append(f"    return -1;")
        ret.append(f"}}")
    elif ArgType.INT == arg.type:
        ret.append(f"{arg.var_name} = strtol({optarg}, &endptr, 0);")
        ret.append(f"if (endptr && (*endptr != '\\0'))")
        ret.append(f"{{")
        ret.append(f"    printf(\"{desc} requires an integer argument\\n\");")
        ret.append(f"    return -1;")
        ret.append(f"}}")
    elif ArgType.FILE == arg.type:
        ret.append(f"{arg.var_name} = {optarg};")
    elif ArgType.STRING == arg.type:
        ret.append(f"{arg.var_name} = {optarg};")

        if type(arg.value) == list:
            ret.append(f"for (int i = 0; i < {len(arg.value)}; i++)")
            ret.append(f"{{")
            ret.append(f"    if (0 == strcmp({arg.var_name}_choices[i], {arg.var_name}))")
            ret.append(f"    {{")
            ret.append(f"        break;")
            ret.append(f"    }}")
            ret.append(f"    if (i == {len(arg.value) - 1})")
            ret.append(f"    {{")
            ret.append(f"        printf(\"{desc} must be one of {arg.value}\\n\");")
            ret.append(f"        return -1;")
            ret.append(f"    }}")
            ret.append(f"}}")

    return ret

def _generate_c_getopt_code(processed_args, getopt_string, opts, positionals, has_longopts):
    ret = ""
    needs_endptr = False

    for arg in processed_args:
        if arg.type in [ArgType.INT, ArgType.FLOAT]:
            needs_endptr = True
            break

    if needs_endptr:
        ret += "    char *endptr = NULL;\n"

    if opts:
        ret += "    int ch;\n\n"

    if opts:
        if has_longopts:
            ret += f"    while ((ch = getopt_long(argc, argv, \"{getopt_string}\", long_options, NULL)) != -1)\n"
        else:
            ret += f"    while ((ch = getopt(argc, argv, \"{getopt_string}\")) != -1)\n"

        ret += f"    {{\n"
        ret += f"        switch (ch)\n"
        ret += f"        {{\n"

        for arg in opts:
            ret += f"            case '{arg.opt[1]}':\n"
            ret += f"            {{\n"

            ret += '\n'.join(["                " + x for x in _generate_c_opt_lines(arg)])
            ret += '\n'

            ret += f"                break;\n"
            ret += f"            }}\n"

        ret += f"        }}\n"
        ret += f"    }}\n\n"

        if positionals:
            # Has both positionals and opts
            ret += f"    if (argc < (optind + {len(positionals)}))\n"
            ret += f"    {{\n"
            ret += f"        printf(\"Missing positional arguments\\n\");\n"
            ret += f"        return -1;\n"
            ret += f"    }}\n\n"

            for i in range(len(positionals)):
                arg = positionals[i]
                desc = f"Positional argument #{i + 1} ({arg.var_name})"
                optarg = f"argv[optind]"
                ret += '\n'.join(["    " + x for x in _generate_c_opt_lines(arg, desc, optarg)])

                if i < (len(positionals) - 1):
                    ret += "\n    optind++;"

                ret += "\n\n"

            pass

    elif positionals:
        # Has only positionals and no opts
        ret += f"    if (argc < {len(positionals) + 1})\n"
        ret += f"    {{\n"
        ret += f"        printf(\"Missing positional arguments\\n\");\n"
        ret += f"        return -1;\n"
        ret += f"    }}\n\n"

        for i in range(len(positionals)):
            arg = positionals[i]
            desc = f"Positional argument #{i + 1} ({arg.var_name})"
            optarg = f"argv[{i + 1}]"
            ret += '\n'.join(["    " + x for x in _generate_c_opt_lines(arg, desc, optarg)])
            ret += "\n\n"

    ret += f"    return 0;"

    return ret

def _generate_c_print_code(processed_args):
    ret = ""

    for arg in processed_args:
        format_arg = ""
        var_name = ""

        if arg.is_flag():
            format_arg = "%s"
            var_name = f"{arg.var_name} ? \"true\" : \"false\""
        elif arg.type == ArgType.INT:
            format_arg = "%ld"
            var_name = f"{arg.var_name}"
        elif arg.type == ArgType.FLOAT:
            format_arg = "%.4f"
            var_name = f"{arg.var_name}"
        elif arg.type in [ArgType.FILE, ArgType.STRING]:
            format_arg = "%s"
            var_name = f"{arg.var_name} ? {arg.var_name} : \"null\""

        ret += f"    printf(\"{arg.desc}: {format_arg}\\n\", {var_name});\n"

    return ret + "\n"

def _generate_c_usage_code(processed_args):
    lines = []
    positionals = []
    opts = []

    for arg in processed_args:
        if arg.is_positional():
            positionals.append(arg)
        else:
            opts.append(arg)

    lines.append("\"\\n\"")
    lines.append("\"USAGE:\\n\\n\"")

    line = "program_name"
    if opts:
        line += " [OPTIONS]"

    if positionals:
        positional_names = ' '.join([x.var_name for x in positionals])
        line += f" {positional_names}"

    lines.append("\"" + line + "\\n\"")

    if opts:
        lines.append("\"\\nOPTIONS:\\n\\n\"")
        longest_left_col = 0
        usage_lines = []

        for opt in opts:
            left_col = "\"" + opt.opt
            if opt.longopt is not None:
                left_col += " " + opt.longopt

            arg = None
            right_col = ""
            if opt.is_flag():
                right_col = f"{opt.desc} flag\\n\""
            else:
                if type(opt.value) == list:
                    right_col = f"A string value (default: %s)\\n\", {opt.var_name} ? {opt.var_name} : \"null\""
                    choices = '|'.join(opt.value)
                    arg = f" [{choices}]"
                elif ArgType.INT == opt.type:
                    right_col = f"An int value (default: %ld)\\n\", {opt.var_name}"
                    arg = " [int]"
                elif ArgType.FLOAT == opt.type:
                    right_col = f"A float value (default: %.2f)\\n\", {opt.var_name}"
                    arg = " [float]"
                elif ArgType.STRING == opt.type:
                    right_col = f"A string value (default: %s)\\n\", {opt.var_name} ? {opt.var_name} : \"null\""
                    arg = " [string]"
                elif ArgType.FILE == opt.type:
                    right_col = f"A filename (default: %s)\\n\", {opt.var_name} ? {opt.var_name} : \"null\""
                    arg = " FILE"

            if arg is not None:
                left_col += arg

            if len(left_col) > longest_left_col:
                longest_left_col = len(left_col)

            usage_lines.append((left_col, right_col))

        for leftcol, rightcol in usage_lines:
            num_spaces = (longest_left_col + 2) - len(leftcol)
            lines.append(leftcol + (" " * num_spaces) + rightcol)

    lines.append("\"\\n\"")

    return '\n'.join([f"    printf({line});" for line in lines])

def generate_c_code(argv=sys.argv):
    """
    Process all command line arguments and return the text of a C program
    which handles the described command-line options

    :param list processed_args: List of CmdlineOpt instances

    :return: text of the corresponding C program
    :rtype: str
    """
    processed_args = process_args(_is_c_reserved_str, argv)

    long_opts = []
    has_flags = False
    has_choices = False
    opts = []
    positionals = []
    decls = ""
    getopt_string = ""

    for arg in processed_args:
        typename = arg.type
        varname = arg.var_name
        value = arg.value

        if arg.is_positional():
            positionals.append(arg)
        else:
            opts.append(arg)

        if arg.is_flag():
            typename = "bool"
            value = "false"
            has_flags = True

        elif arg.type == ArgType.INT:
            typename = "long int"

        elif arg.type in [ArgType.STRING, ArgType.FILE]:
            typename = "char"
            varname = "*" + varname
            value = f"\"{value}\""

            if arg.type == ArgType.FILE:
                if arg.value == "FILE":
                    value = "NULL"
            else:
                # ArgType.STRING
                choices = arg.value.split(',')
                if len(choices) > 1:
                    arg.value = choices
                    value = f"\"{choices[0]}\""
                    choicestrings = ", ".join([f"\"{c}\"" for c in choices])
                    decls += f"static char *{arg.var_name}_choices[] = {{{choicestrings}}};\n"
                    has_choices = True

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
    env_comment = os.environ.get("DUCKARGS_COMMENT", 1)
    try:
        env_comment_int = int(env_comment)
    except ValueError:
        raise RuntimeError("DUCKARGS_COMMENT must be an integer")

    if env_comment_int > 0:
        comment_header = (f"// Generated by duckargs, invoked with the following arguments:\n// " +
                          ' '.join(argv[1:]) + "\n\n")

    CmdlineOpt.positional_count = 0

    if has_flags:
        comment_header += "#include <stdbool.h>\n"

    if opts:
        comment_header += "#include <getopt.h>\n"

    if has_choices:
        comment_header += "#include <string.h>\n"

    parsing_code = _generate_c_getopt_code(processed_args, getopt_string, opts,
                                           positionals, len(long_opts) > 0)

    print_code = ""
    env_print = os.environ.get('DUCKARGS_PRINT', 1)
    try:
        env_print_int = int(env_print)
    except ValueError:
        raise RuntimeError("DUCKARGS_PRINT must be an integer")

    if env_print_int > 0:
        print_code = _generate_c_print_code(processed_args)

    usage_code = _generate_c_usage_code(processed_args)

    return C_TEMPLATE.format(comment_header, decls, usage_code, parsing_code, print_code)
