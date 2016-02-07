# -*- coding: utf-8 -*-

import os
import time
import shutil
import operator
import subprocess

from distutils.dir_util import copy_tree
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from teax import __version__, conf, tty, TEAX_WORK_PATH
from teax.utils.trash import show_messages
from teax.system import engines, plugins
from teax.messages import T_FILE_NOT_EXISTS
from teax.system.parser import LaTeXFilter

class CoreController:
    """
    PREPARE
    ---> rewrite filename -> basename
    ---> check filename, which engine --> @VAR_1
    ---> check if we have this engine @VAR_1
        if not: error/installation guide
    ---> read conf['build'] for:
        --watch - dynamic reload
    PROCEDURES
    ---> copy . to .teax local/working directory
    ---> first run @VAR_1
    ---> find cycles/plugins/queue
        1. look for \bibliography | (.bib, .bcf) --> bibtex/biblatex/biber
        2. look for \usepackage (*) {makeidx} | (.idx) --> makeindex
        3. look for \usepackage (*) {glossaries} | (.glo) --> makeglossaries
    ---> analyze figures [.svg, .png, .jpg] convert to .pdf
    FINAL
    ---> execute queue
        if already successful, copy pdf file locally
    ---> parse stream/result log
        if magic commands 'rerun', 'recompile' return to PROCEDURES
    """
    DEBUG = True

    def __init__(self):
        self.shelf = {'filename': None, 'engine': None}
        self.basename = ''
        self.pdf = True
        self.queue = []

    def mount(self, filename):
        copy_tree(TEAX_WORK_PATH, TEAX_WORK_PATH + '/.teax/')

        if not os.path.splitext(filename)[1]:
            filename = os.path.basename(filename) + '.tex'
        if not os.path.isfile(filename):
            tty.errn(T_FILE_NOT_EXISTS % filename)
        self.shelf['filename'] = filename

        engines_list = engines.analyze(filename)
        engine = max(engines_list.iteritems(), key=operator.itemgetter(1))[0]
        self.shelf['engine'] = engine

        self.basename = os.path.splitext(filename)[0]

    def build(self, pdf=True):
        self.pdf = pdf
        if self.DEBUG:
            self.__show_debug()
        tty.section('BUILD')
        os.chdir(TEAX_WORK_PATH + '/.teax/')
        engines.provide(self.shelf['filename'], self.shelf['engine'])
        for plugin in plugins.analyze(TEAX_WORK_PATH + '/.teax/'):
            plugins.provide(self.shelf['filename'], plugin)
            engines.provide(self.shelf['filename'], self.shelf['engine'])
            engines.provide(self.shelf['filename'], self.shelf['engine'])
        if self.pdf:
            shutil.copy(self.basename + '.pdf', TEAX_WORK_PATH)
        os.chdir(TEAX_WORK_PATH)

    def result(self):
        basename = self.basename
        logfile = TEAX_WORK_PATH + '/.teax/' + basename + '.log'
        latex_filter = LaTeXFilter()
        latex_filter.feed(open(logfile, 'rt').read())
        show_messages(latex_filter.get_messages())
        if conf['build.watch'] and not conf['process.loop']:
            self.__stay_and_watch()

    def __show_debug(self):
        platform = self.__output(['uname', '-mnprs']).strip()
        tty.echo("Path:     {0}".format(TEAX_WORK_PATH))
        tty.echo("Platform: {0}".format(platform))
        tty.echo("Engine:   {0} [{1}]".format(self.shelf['engine'], __version__))

    def __output(self, cmd):
        """Returns output for the given shell command."""
        return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

    def __stay_and_watch(self):
        process = Observer()
        handler = CoreHandler()
        handler.env(self.shelf['filename'], self.pdf)
        process.schedule(handler, path=TEAX_WORK_PATH)
        process.start()
        conf['process.loop'] = True
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            process.stop()
        process.join()


class CoreHandler(PatternMatchingEventHandler):
    patterns = ["*.tex", "*.bib"]

    def env(self, filename, pdf):
        self.filename = filename
        self.pdf = pdf

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        """
        tty.echo(
            "$[BG_CYAN]%s %s$[NORMAL]" %
            (event.src_path, event.event_type))
        core = CoreController()
        core.mount(self.filename)
        core.build(pdf=self.pdf)
        core.result()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)
