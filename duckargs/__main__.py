import sys
from duckargs import generate_python_code, generate_c_code, __version__

USAGE = """
duckargs %s

Erik K. Nyquist 2023

The purpose of duckargs is to save some typing whenever you want to quickly create
a python program that accepts command line arguments. Just run duckargs with the
options & arguments that you want your program to accept, with example argument
values, and duckargs will generate the python code for a program that uses argparse
to handle those arguments.

For example, running duckargs like this:


    duckargs positional_arg -i --intval 12 -d --floatval 99.9 -f --somefile FILE


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

def main():
    if len(sys.argv) == 1:
        print(USAGE)
        return

    #try:
        #print(generate_python_code())
    print(generate_c_code())
    #except (ValueError, RuntimeError) as e:
    #    print(f"Error: {e}")
    
if __name__ == "__main__":
    main()
