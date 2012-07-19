#!python
# -*- coding: utf-8 -*-
import sys, os, re
from os.path import dirname, abspath, join
from setuptools import setup, find_packages

HERE = abspath(dirname(__file__))
readme = open(join(HERE, 'README.md'), 'rU').read()

package_file = open(join(HERE, 'nesting.py'), 'rU')
__version__ = re.sub(
    r".*\b__version__\s+=\s+'([^']+)'.*",
    r'\1',
    [ line.strip() for line in package_file if '__version__' in line ].pop(0)
)


setup(
    name             = 'nesting',
    version          = __version__,
    description      = 'Operator to construct nested rollups from lists of records.',
    long_description = readme,
    url              = 'https://github.com/dsc/nesting',
    
    author           = 'David Schoonover',
    author_email     = 'dsc@less.ly',
    
    py_modules       = [ 'nesting', ],
    
    keywords         = 'nesting operator data series',
    classifiers      = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe = False,
    license  = "MIT",
)
