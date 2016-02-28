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

class CoreController(object):
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
        self.__shelf = {'filename': None, 'engine': None}
        self.__basename = ''
        self.__pdf = True
        self.__filter = LaTeXFilter()

    def mount(self, filename):
        copy_tree(TEAX_WORK_PATH, TEAX_WORK_PATH + '/.teax/')
        if not os.path.splitext(filename)[1]:
            filename = os.path.basename(filename) + '.tex'
        if not os.path.isfile(filename):
            tty.errn(T_FILE_NOT_EXISTS % filename)
        self.__shelf['filename'] = filename
        engines_list = engines.analyze(filename)
        engine = max(engines_list.iteritems(), key=operator.itemgetter(1))[0]
        self.__shelf['engine'] = engine
        self.__basename = os.path.splitext(filename)[0]

    def build(self, pdf=True):
        self.__pdf = pdf
        if self.DEBUG:
            self.__show_debug()
        tty.section('BUILD')
        os.chdir(TEAX_WORK_PATH + '/.teax/')
        engines.provide(self.__shelf['filename'], self.__shelf['engine'])
        self.__run_plugins()
        if self.__pdf:
            self.__generate_document()
        os.chdir(TEAX_WORK_PATH)

    def result(self):
        logfile = TEAX_WORK_PATH + '/.teax/' + self.__basename + '.log'
        self.__filter.feed(open(logfile, 'rt').read())
        show_messages(self.__filter.get_messages())
        if conf['build.watch'] and not conf['process.loop']:
            self.__stay_and_watch()

    def __generate_document(self):
        if os.path.isfile(self.__basename + '.pdf'):
            shutil.copy(self.__basename + '.pdf', TEAX_WORK_PATH)

    def __run_plugins(self):
        for plugin in plugins.analyze(TEAX_WORK_PATH + '/.teax/'):
            plugins.provide(self.__shelf['filename'], plugin)
            engines.provide(self.__shelf['filename'], self.__shelf['engine'])
            engines.provide(self.__shelf['filename'], self.__shelf['engine'])

    def __show_debug(self):
        platform = self.__output(['uname', '-mnprs']).strip()
        tty.echo("Path:     {0}".format(TEAX_WORK_PATH))
        tty.echo("Platform: {0}".format(platform))
        tty.echo("Engine:   {0} [{1}]".format(self.__shelf['engine'], __version__))

    def __output(self, cmd):
        """Returns output for the given shell command."""
        return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

    def __stay_and_watch(self):
        process = Observer()
        handler = CoreHandler()
        handler.env(self.__shelf['filename'])
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

    def env(self, filename):
        self.__filename = filename

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
        core.build()
        core.result()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)
