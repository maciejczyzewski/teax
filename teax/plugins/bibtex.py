# -*- coding: utf-8 -*-

import os
import subprocess

from teax.system.plugin import PluginObject, PluginFacade

@PluginFacade.register
class BibtexPlugin(PluginObject):
    parseable_extensions = {'.bib', '.bst'}

    def __init__(self, filename):
        self.filename = filename
        self.basename = os.path.splitext(os.path.basename(filename))[0]

    def start(self):
        subprocess.Popen('bibtex ' + self.basename,
            stdout=subprocess.PIPE, shell=True).communicate()[0]

    @classmethod
    def is_active(cls, path):
        for filename in next(os.walk(path))[2]:
            if filename.endswith(tuple(cls.parseable_extensions)):
                return True
        return False
