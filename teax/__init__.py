# -*- coding: utf-8 -*-
"""teax package initialization"""

import os

__version__ = '0.0.dev1'

#== Variables

TEAX_WORK_PATH = os.getcwd()
TEAX_REAL_PATH = os.path.dirname(os.path.realpath(__file__))

#== Environment

os.chdir(TEAX_WORK_PATH)

#== Terminal (input/output)

from teax.terminal import TerminalObject
tty = TerminalObject()

#== Configuration

from teax.config import ConfigObject
conf = ConfigObject('teax.ini')

#== System/Core

import teax.system
