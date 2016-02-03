# -*- coding: utf-8 -*-

import os
import subprocess

from teax.system.engine import EngineObject, EngineFacade

@EngineFacade.register
class ContextEngine(EngineObject):
    parseable_extensions = {'.context', '.tex'}

    def __init__(self, filename):
        self.filename = filename

    def start(self):
        subprocess.Popen('texexec ' + os.path.basename(self.filename),
            stdout=subprocess.PIPE, shell=True).communicate()[0]

    @classmethod
    def match(cls, filename, points=0):
        source = open(filename, 'rt').read()
        if filename.endswith(tuple(cls.parseable_extensions)):
            points += 1
        if '\starttext' in source or '\stoptext' in source:
            points += 1
        return points
