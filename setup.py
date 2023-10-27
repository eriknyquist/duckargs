import unittest
import os
from setuptools import setup
from distutils.core import Command

from duckargs import __version__

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, "README.rst")

class RunDuckargsTests(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        suite = unittest.TestLoader().discover("tests")
        t = unittest.TextTestRunner(verbosity = 2)
        t.run(suite)

with open(README, 'r') as f:
    long_description = f.read()

setup(
    name='duckargs',
    version=__version__,
    description=('Code generation tool, creates python / C programs that parse command line arguments. '
                 'Say goodbye to starting each project by reading "argparse" / "geptopt.h" docs.'),
    long_description=long_description,
    url='http://github.com/eriknyquist/duckargs',
    author='Erik Nyquist',
    author_email='eknyquist@gmail.com',
    license='Apache 2.0',
    packages=['duckargs'],
    cmdclass={'test': RunDuckargsTests},
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'duckargs=duckargs.__main__:duckargs_python',
            'duckargs-c=duckargs.__main__:duckargs_c',
            'duckargs-python=duckargs.__main__:duckargs_python'
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    project_urls={
        "Documentation": "https://github.com/eriknyquist/duckargs",
        "Issues": "https://github.com/eriknyquist/duckargs/issues",
        "Contributions": "https://github.com/eriknyquist/duckargs/pulls"
    }
)
