#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""teax setup environment"""

import sys

from setuptools import setup, find_packages

from teax import __version__
from teax.__pkginfo__ import LICENSE, DISTNAME, AUTHOR, EMAIL, URL, \
    DESCRIPTION, LONG_DESCRIPTION, CLASSIFIERS

if sys.version_info[:2] < (2, 6):
    sys.exit('Error: requires python 2.6 or higher...')

setup(
    name=DISTNAME,
    version=__version__,
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'tox>=2.3.1',      # Packages that are needed,
        'pep8>=1.7.0',     # if you are a contributor.
        'pytest>=2.8.5',   # Temporarily, let them be.
        'click>=2.0',
        'watchdog>=0.8.3'
    ],
    classifiers=CLASSIFIERS,
    entry_points='''
        [console_scripts]
        teax=teax.interface:teax
    '''
)
