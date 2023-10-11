duckargs
========

.. |tests_badge| image:: https://github.com/eriknyquist/duckargs/actions/workflows/tests.yml/badge.svg
.. |cov_badge| image:: https://github.com/eriknyquist/duckargs/actions/workflows/coverage.yml/badge.svg
.. |version_badge| image:: https://badgen.net/pypi/v/duckargs
.. |license_badge| image:: https://badgen.net/pypi/license/duckargs

|tests_badge| |cov_badge| |version_badge| |license_badge|

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

    $ python -m duckargs positional_arg1 positional_arg2 -i --int-val 4 -f 3.3 -f --file FILE -F --otherfile FILE -a -b -c


The output of the above command looks like this:


.. code:: python

    # positional_arg1 positional_arg2 -i --int-val 4 -f 3.3 -f --file FILE -F --otherfile FILE -a -b -c

    import argparse

    def main():
        parser = argparse.ArgumentParser(description='',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('positional_arg1', help='a string')
        parser.add_argument('positional_arg2', help='a string')
        parser.add_argument('-i', '--int-val', default=4, type=int, help='an int value')
        parser.add_argument('-f', default=3.3, type=float, help='a float value')
        parser.add_argument('-f', '--file', default=None, type=argparse.FileType(), help='a filename')
        parser.add_argument('-F', '--otherfile', default=None, type=argparse.FileType(), help='a filename')
        parser.add_argument('-a', action='store_true', help='a flag')
        parser.add_argument('-b', action='store_true', help='b flag')
        parser.add_argument('-c', action='store_true', help='c flag')
        args = parser.parse_args()

        print(args.positional_arg1)
        print(args.positional_arg2)
        print(args.int_val)
        print(args.f)
        print(args.file)
        print(args.otherfile)
        print(args.a)
        print(args.b)
        print(args.c)

    if __name__ == "__main__":
        main()

Comma-separated choices for option argument
===========================================

If you have an option which accepts an argument, and you write an argument string with
multiple values separated by commas (e.g. ``-m --mode active,idle,sim``), then ``duckargs``
will use the comma-separated values as a ``choices`` list for argparse, e.g.:

::

    parser.add_argument('-m', '--mode', choices=['active', 'idle', 'sim'], default='active', help='a string')

Filenames for option arguments
==============================

If you have an option that you want to accept a filename, you have two ways to tell
``duckargs`` that the option argument should be treated as a file:

* Pass the path to a file that actually exists (e.g. ``-f --filename file.txt``)
  as the option argument

* Pass ``FILE`` as the option argument (e.g. ``-f --filename FILE``)

Either of which will generate a line like this:

::

    parser.add_argument('-f', '--filename', default='file', type=argparse.FileType(), help='a filename')


Use duckargs in python code
===========================

If you want to use duckargs in your own script, you can use the ``duckargs.generate_python_code`` function,
which accepts a list of command line arguments:

.. code:: python

    import sys
    from duckargs import generate_python_code

    python_code = generate_python_code(sys.argv)

Pitfalls
========

If you have a combination of flags and positional arguments, and you happen to have a flag
followed by a positional argument (as in: ``python -m duckargs -q --quiet positional_arg``),
``duckargs`` has no way to tell that you wanted a positional arg, so it will assume you want
an option ``-q --quiet`` with a required argument.

To avoid this, it is recommended to declare your positional arguments first (as in: ``python -m duckargs positional_arg -q --quiet``)
