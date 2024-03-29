.. contents:: **Table of Contents**

.. |duck| unicode:: 0x1F986

duckargs |duck|
---------------

.. |tests_badge| image:: https://github.com/eriknyquist/duckargs/actions/workflows/tests.yml/badge.svg
.. |cov_badge| image:: https://github.com/eriknyquist/duckargs/actions/workflows/coverage.yml/badge.svg
.. |version_badge| image:: https://badgen.net/pypi/v/duckargs
.. |license_badge| image:: https://badgen.net/pypi/license/duckargs
.. |downloads_badge| image:: https://static.pepy.tech/badge/duckargs
.. |conda_badge| image:: https://img.shields.io/conda/dn/conda-forge/duckargs.svg?label=conda-forge

|tests_badge| |cov_badge| |version_badge| |license_badge| |downloads_badge| |conda_badge|

Brief description
=================

The purpose of ``duckargs`` is to save some typing whenever you want to quickly
create a python program or C program that accepts command line arguments. Just run
``duckargs`` (generates python), ``duckargs-python`` (also generates python) or
``duckargs-c`` (generates C) with all the options/arguments that you want your program
to accept, and ``duckargs`` will print the code for a program that handles those
options/arguments.

Longer description
==================

If you're like me, then you often need to create little throwaway command-line tools,
but *not* often enough to remember the exact syntax/details of ``argparse`` or ``getopt.h``,
so you often start these efforts by looking up the relevant docs and refreshing your memory.

Next, you spend some time typing out the boilerplate arg-parsing code, with one eye
on the docs, and eventually (depending on how much arg-parsing boilerplate code you need)
you may forget some interesting detail that was part of your original idea, or you may
just get sick of it and decide that you don't event *need* a command-line tool, and
you'll do the thing manually instead.

``duckargs`` makes this process a little bit simpler, and shortens the time between your
idea and having a working C or Python program.

Let's imagine that you want to create a little command-line tool that accepts the
following command line options/arguments:

* A positional argument, string
* An optional integer value (``-i`` or ``--intval``)
* An optional float value (``-f`` or ``--floatval``)
* A flag (``-q``)

You can run ``duckargs`` and pass all those options/arguments/flags, and ``duckargs`` will
generate a working program with all the boilerplate taken care of:

**Generating Python**

.. code::

    $ duckargs somestring -i --intval 99 -f --floatval 7.7 -q

**Output**

.. code::

    # Generated by duckargs, invoked with the following arguments:
    # somestring -i --intval 99 -f --floatval 7.7 -q

    import argparse

    def main():
        parser = argparse.ArgumentParser(description='A command-line program generated by duckargs',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('somestring', help='a string')
        parser.add_argument('-i', '--intval', default=99, type=int, help='an int value')
        parser.add_argument('-f', '--floatval', default=7.7, type=float, help='a float value')
        parser.add_argument('-q', action='store_true', help='q flag')
        args = parser.parse_args()

        print(args.somestring)
        print(args.intval)
        print(args.floatval)
        print(args.q)

    if __name__ == "__main__":
        main()

**Generating C**

.. code::

    $ duckargs-c somestring -i --intval 99 -f --floatval 7.7 -q

**Output**

.. code::

    // Generated by duckargs, invoked with the following arguments:
    // somestring -i --intval 99 -f --floatval 7.7 -q

    #include <stdbool.h>
    #include <getopt.h>
    #include <stdlib.h>
    #include <stdio.h>

    static char *somestring = "somestring";
    static long int intval = 99;
    static float floatval = 7.7;
    static bool q = false;

    static struct option long_options[] =
    {
        {"intval", required_argument, NULL, 'i'},
        {"floatval", required_argument, NULL, 'f'},
        {NULL, 0, NULL, 0}
    };

    void print_usage(void)
    {
        printf("\n");
        printf("USAGE:\n\n");
        printf("program_name [OPTIONS] somestring\n");
        printf("\nOPTIONS:\n\n");
        printf("-i --intval [int]      An int value (default: %ld)\n", int);
        printf("-f --floatval [float]  A float value (default: %.2f)\n", float);
        printf("-q                     A flag\n");
        printf("\n");
    }

    int parse_args(int argc, char *argv[])
    {
        char *endptr = NULL;
        int ch;

        while ((ch = getopt_long(argc, argv, "i:f:q", long_options, NULL)) != -1)
        {
            switch (ch)
            {
                case 'i':
                {
                    intval = strtol(optarg, &endptr, 0);
                    if (endptr && (*endptr != '\0'))
                    {
                        printf("Option '-i' requires an integer argument\n");
                        return -1;
                    }
                    break;
                }
                case 'f':
                {
                    floatval = strtof(optarg, &endptr);
                    if (endptr == optarg)
                    {
                        printf("Option '-f' requires a floating-point argument\n");
                        return -1;
                    }
                    break;
                }
                case 'q':
                {
                    q = true;
                    break;
                }
            }
        }

        if (argc < (optind + 1))
        {
            printf("Missing positional arguments\n");
            return -1;
        }

        somestring = argv[optind];

        return 0;
    }

    int main(int argc, char *argv[])
    {
        if (argc < 2)
        {
            print_usage();
            return -1;
        }

        int ret = parse_args(argc, argv);
        if (0 != ret)
        {
            return ret;
        }

        printf("somestring: %s\n", somestring ? somestring : "null");
        printf("intval: %ld\n", intval);
        printf("floatval: %.4f\n", floatval);
        printf("q: %s\n", q ? "true" : "false");

        return 0;
    }

Install
=======

Install with pip (python 3x required):

::

    pip install duckargs

Comma-separated choices for option argument
===========================================

If you have an option which accepts an argument, and you write an argument string with
multiple values separated by commas (e.g. ``-m --mode active,idle,sim``), then generated 
python code will use the comma-separated values as a ``choices`` list for argparse:

.. code:: python

    parser.add_argument('-m', '--mode', choices=['active', 'idle', 'sim'], default='active', help='a string')

And generated C code will use the comma-separated values to restrict values in a similar manner:

.. code:: c

    static char *mode_choices[] = {"active", "idle", "stop"};
    static char *mode = "active";

    static struct option long_options[] =
    {
        {"mode", required_argument, NULL, 'm'},
        {NULL, 0, NULL, 0}
    };

    void print_usage(void)
    {
        printf("\n");
        printf("USAGE:\n\n");
        printf("program_name [OPTIONS]\n");
        printf("\nOPTIONS:\n\n");
        printf("-m --mode [active|idle|stop]  A string value (default: %s)\n", mode ? mode : "null");
        printf("\n");
    }

    int parse_args(int argc, char *argv[])
    {
        int ch;

        while ((ch = getopt_long(argc, argv, "m:", long_options, NULL)) != -1)
        {
            switch (ch)
            {
                case 'm':
                {
                    mode = optarg;
                    for (int i = 0; i < 3; i++)
                    {
                        if (0 == strcmp(mode_choices[i], mode))
                        {
                            break;
                        }
                        if (i == 2)
                        {
                            printf("Option '-m' must be one of ['active', 'idle', 'stop']\n");
                            return -1;
                        }
                    }
                    break;
                }
            }
        }

        return 0;
    }

Filenames for option arguments
==============================

If you have an option that you want to accept a filename, you have two ways to tell
``duckargs`` that the option argument should be treated as a file:

* Pass the path to a file that actually exists (e.g. ``-f --filename file.txt``)
  as the option argument

* Pass ``FILE`` as the option argument (e.g. ``-f --filename FILE``)

Either of which will generate python code like this:

.. code:: python

    parser.add_argument('-f', '--filename', default='file', type=argparse.FileType(), help='a filename')

And will generate C code like this:

.. code:: c

    static char *filename = NULL;

    static struct option long_options[] =
    {
        {"filename", required_argument, NULL, 'f'},
        {NULL, 0, NULL, 0}
    };

    void print_usage(void)
    {
        printf("\n");
        printf("USAGE:\n\n");
        printf("program_name [OPTIONS]\n");
        printf("\nOPTIONS:\n\n");
        printf("-f --filename FILE  A filename (default: %s)\n", filename ? filename : "null");
        printf("\n");
    }

    int parse_args(int argc, char *argv[])
    {
        int ch;

        while ((ch = getopt_long(argc, argv, "f:", long_options, NULL)) != -1)
        {
            switch (ch)
            {
                case 'f':
                {
                    filename = optarg;
                    break;
                }
            }
        }

        return 0;
    }

Environment variables
=====================

Some things can be configured by setting environment variables.

``DUCKARGS_PRINT``
##################

By default, ``duckargs`` generates a program that prints all provided arguments/options
to stdout after argument parsing is complete.
If you want to disable this and generate programs without the print statements, set
``DUCKARGS_PRINT=0`` in your environment variables. This environment variable affects
generated C code and generated python code.

``DUCKARGS_COMMENT``
####################

By default, ``duckargs`` generates a program that prints a comment header at the top,
showing the arguments that ``duckargs`` was invoked with. If you want to disable this and
generate programs without the comment header, set ``DUCKARGS_COMMENT=0`` in your environment
variables. This environment variable affects generated C code and generated python code.

Use duckargs in python code
===========================

If you want to use duckargs in your own script, you can use the ``duckargs.generate_python_code`` and
``duckargs.generate_c_code`` functions, both of which accept a list of command line arguments:

.. code:: python

    import sys
    from duckargs import generate_python_code, generate_c_code

    python_code = generate_python_code(sys.argv)

    c_code = generate_c_code(sys.argv)

Pitfalls
========

If you have a combination of flags and positional arguments, and you happen to have a flag
followed by a positional argument (as in: ``python -m duckargs -q --quiet positional_arg``),
``duckargs`` has no way to tell that you wanted a positional arg, so it will assume you want
an option ``-q --quiet`` with a required argument.

To avoid this, it is recommended to declare your positional arguments first (as in: ``python -m duckargs positional_arg -q --quiet``)

Contributions
=============

Contributions are welcome, please open a pull request at `<https://github.com/eriknyquist/duckargs/pulls>`_.
You will need to install packages required for development by doing ``pip install -r dev_requirements.txt``.

Please ensure that all existing tests pass, new test(s) are added if required, and the code coverage
check passes.

* Run tests with ``python setup.py test``.
* Run tests and and generate code coverage report with ``python code_coverage.py``
  (this script will report an error if coverage is below 95%)

If you have any questions about / need help with contributions or tests, please
contact Erik at eknyquist@gmail.com.
