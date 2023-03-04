duckargs
========

The purpose of this package is to save some typing whenever you want to quickly
create a python program that accepts command line arguments. Just run ``duckargs``
with the arguments that you want your program to accept, with example values for
options, and ``duckargs`` will generate the python code for a program that uses
``argparse`` to handle those arguments.

Example
=======

::
	$ python -m duckargs -i --intval 4 -f --floatval 3.3 -F --file testfile -a -b -c positional_arg

	import argparse

	def main():
		parser = argparse.ArgumentParser(description='',
										 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

		parser.add_argument('-i', '--intval', default=4, type=int, help='an int value')
		parser.add_argument('-f', '--floatval', default=3.3, type=float, help='a float value')
		parser.add_argument('-F', '--file', default='testfile', type=argparse.FileType('w'), help='a filename')
		parser.add_argument('-a', action='store_true')
		parser.add_argument('-b', action='store_true')
		parser.add_argument('-c', default='positional_arg', help='a string')
		args = parser.parse_args()

	if __name__ == "__main__":
		main()