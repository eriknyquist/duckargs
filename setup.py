import unittest
import os
from setuptools import setup
from distutils.core import Command

from duckargs import __version__

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, "README.rst")

with open(README, 'r') as f:
    long_description = f.read()

setup(
    name='duckargs',
    version=__version__,
    description=('Productivity tool for quickly creating python programs that parse command-line arguments'),
    long_description=long_description,
    url='http://github.com/eriknyquist/duckargs',
    author='Erik Nyquist',
    author_email='eknyquist@gmail.com',
    license='Apache 2.0',
    packages=['duckargs'],
    include_package_data=True,
    zip_safe=False,
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
