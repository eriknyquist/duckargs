import sys
from duckargs import generate_python_code, generate_c_code, __version__

PYTHON_USAGE = """
duckargs-python %s

Erik K. Nyquist 2023

The purpose of duckargs-python is to save some typing whenever you want to quickly create
a python program that accepts command line arguments. Just run duckargs-python with all the
options & arguments that you want your program to accept, and duckargs-python will print
the python code for a program that uses argparse to handle those options & arguments.

For example, running duckargs-python like this:


    duckargs-python positional_arg -i --intval 12 -d --floatval 99.9 -f --somefile FILE


Prints the following python code:


    import argparse

    def main():
	parser = argparse.ArgumentParser(description='',
					 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	parser.add_argument('positional_arg', help='a string')
	parser.add_argument('-i', '--intval', default=12, type=int, help='an int value')
	parser.add_argument('-d', '--floatval', default=99.9, type=float, help='a float value')
	parser.add_argument('-f', '--somefile', default=None, type=argparse.FileType(), help='a filename')
	args = parser.parse_args()

	print(args.positional_arg)
	print(args.intval)
	print(args.floatval)
	print(args.somefile)

    if __name__ == "__main__":
	main()

""" % __version__

C_USAGE = """
duckargs-c %s

Erik K. Nyquist 2023

The purpose of duckargs-c is to save some typing whenever you want to quickly create
a C program that accepts command line arguments. Just run duckargs-c with the options &
arguments that you want your program to accept, and duckargs-c will generate the C code
for a program that uses getopt.h to handle those options & arguments.

For example, running duckargs-c like this:


    duckargs-c positional_arg -i --intval 12 -d --floatval 99.9 -f --somefile FILE


Prints the C code for a command-line program which accepts arguments in the following
manner:

program_name [OPTIONS] positional_arg

-i --intval [int]      An int value (default: 12)
-d --floatval [float]  A float value (default: 99.9)
-f --somefile FILE     A filename (default: null)

""" % __version__

def duckargs_python():
    """
    CLI entry point for 'duckargs-python'
    """
    if len(sys.argv) == 1:
        print(PYTHON_USAGE)
        return

    try:
        print(generate_python_code())
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")

def duckargs_c():
    """
    CLI entry point for 'duckargs-c'
    """
    if len(sys.argv) == 1:
        print(C_USAGE)
        return

    try:
        print(generate_c_code())
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    duckargs_python()
