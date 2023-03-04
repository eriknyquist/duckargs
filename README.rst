duckargs
========

The purpose of this package is to save some typing whenever you want to quickly
create a python program that accepts command line arguments. Just run ``duckargs``
with the arguments that you want your program to accept, with example values for
options, and ``duckargs`` will generate the python code for a program that uses
``argparse`` to handle those arguments.

Install
=======

Install with pip (python 3x required):

::

    pip install duckargs

Example
=======

Run duckargs from the command line via ``python -m duckargs``, followed by whatever arguments/options/flags
you want your program to accept, and ``duckargs`` will print the corresponding python code.

::

    $ python -m duckargs positional_arg1 positional_arg2 -i --intval 4 -f 3.3 -F --file file_that_exists -a -b -c

    import argparse

    def main():
        parser = argparse.ArgumentParser(description='',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('positional_arg1', help='a string')
        parser.add_argument('positional_arg2', help='a string')
        parser.add_argument('-i', '--intval', default=4, type=int, help='an int value')
        parser.add_argument('-f', default=3.3, type=float, help='a float value')
        parser.add_argument('-F', '--file', default='file_that_exists', help='a string')
        parser.add_argument('-a', action='store_true')
        parser.add_argument('-b', action='store_true')
        parser.add_argument('-c', action='store_true')
        args = parser.parse_args()

    if __name__ == "__main__":
        main()

Pitfalls
========

If you have a combination of flags and positional arguments, and you happen to have a flag
followed by a positional argument (as in: ``python -m duckargs -q --quiet positional_arg``),
``duckargs`` has no way to tell that you wanted a positional arg, so it will assume you want
an option ``-q --quiet`` with a required argument.

To avoid this, it is recommended to declare your positional arguments first (as in: ``python -m duckargs positional_arg -q --quiet``)
