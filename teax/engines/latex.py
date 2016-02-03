# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess

from teax.system.engine import EngineObject, EngineFacade

@EngineFacade.register
class LatexEngine(EngineObject):
    parseable_extensions = {'.latex', '.tex'}

    flags = [
        '-interaction nonstopmode',
        '-halt-on-error',
        '-file-line-error']

    def __init__(self, filename):
        self.filename = filename

    def start(self):
        # print("=== LATEX ADAPTER ===")
        # subprocess.Popen('pdflatex ' + os.path.basename(self.filename),
        #     stdout=subprocess.PIPE, shell=True).communicate()[0]
        # Virtual LaTeX file, in our local cache
        _ftex = os.path.basename(self.filename)
        # Command for compiling LaTeX document
        _cmd = ' '.join(['pdflatex'] + self.flags + [_ftex])
        # Preparing bridge (papir <--> latex), communication
        p = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE)
        # Grab stdout line by line as it becomes available.  This will loop until
        # p terminates.
        while p.poll() is None:
            # This blocks until it receives a newline,
            # and sends it to local LaTeX parser.
            self.parser(p.stdout.readline())
        # When the subprocess terminates there might be unconsumed output
        # that still needs to be processed.
        print(p.stdout.read())

    def parser(self, line):
        """
        Interprets the line of LaTeX/TeX output. Each line has assigned
        symbol (i.e., 'W' means something is wrong, something missing).
        """
        if re.search(r"(?i)(.)" + "rerun " + "(.*)", line):
            pass # self.STATUS['stream'] = False
        if re.search(r"(?i)(.)" + "warning" + "(.*)", line):
            sys.stdout.write('W')
        elif re.search(r"(?i)(.)" + "error" + "(.*)", line):
            sys.stdout.write('E')
            pass # self.STATUS['stream'] = False
        else:
            sys.stdout.write('.')

    @classmethod
    def match(cls, filename, points=0):
        source = open(filename, 'rt').read()
        if filename.endswith(tuple(cls.parseable_extensions)):
            points += 1
        if '\documentclass' in source:
            points += 1
        return points
