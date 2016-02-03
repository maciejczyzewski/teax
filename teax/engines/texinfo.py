# -*- coding: utf-8 -*-

import os
import subprocess

from teax.system.engine import EngineObject, EngineFacade

@EngineFacade.register
class TexinfoEngine(EngineObject):
    parseable_extensions = {'.texinfo', '.texi'}

    def __init__(self, filename):
        self.filename = filename

    def start(self):
        subprocess.Popen('makeinfo ' + os.path.basename(self.filename),
            stdout=subprocess.PIPE, shell=True).communicate()[0]

    @classmethod
    def match(cls, filename, points=0):
        source = open(filename, 'rt').read()
        if filename.endswith(tuple(cls.parseable_extensions)):
            points += 1
        if '@bye' in source:
            points += 1
        if '\input texinfo' in source:
            points += 1
        if '-*-texinfo-*-' in source or '-*- texinfo -*-' in source:
            points += 1
        return points
