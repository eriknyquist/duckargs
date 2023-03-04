duckargs
========

The purpose of this package is to save some typing whenever you want to quickly
create a python program that accepts command line arguments. Just run ``duckargs``
with the arguments that you want your program to accept, with example values for
options, and ``duckargs`` will generate the python code for a program that uses
``argparse`` to handle those arguments.

Example
=======

Run duckargs from the command line via ``python -m duckargs``, followed by whatever arguments/options/flags
you want your program to accept, and ``duckargs`` will print the corresponding python code.

::

    $ python -m duckargs -i --intval 4 -f 3.3 -F --file file_that_exists -a -b -c positional_arg

    import argparse

    def main():
        parser = argparse.ArgumentParser(description='',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('-i', '--intval', default=4, type=int, help='an int value')
        parser.add_argument('-f', default=3.3, type=float, help='a float value')
        parser.add_argument('-F', '--file', default='file_that_exists', type=argparse.FileType('w'), help='a filename')
        parser.add_argument('-a', action='store_true')
        parser.add_argument('-b', action='store_true')
        parser.add_argument('-c', default='positional_arg', help='a string')
        args = parser.parse_args()

    if __name__ == "__main__":
        main()
