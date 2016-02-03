# -*- coding: utf-8 -*-

import os
import shutil
import operator

from distutils.dir_util import copy_tree

from teax import conf, tty, TEAX_WORK_PATH
from teax.system import engines, plugins
from teax.messages import T_FILE_NOT_EXISTS

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
    def __init__(self):
        self.shelf = {'filename': None, 'engine': None}
        self.queue = []

    def mount(self, filename):
        copy_tree(TEAX_WORK_PATH, TEAX_WORK_PATH + '/.teax/')

        if not os.path.splitext(filename)[1]:
            filename = os.path.basename(filename) + '.tex'
        if not os.path.isfile(filename):
            tty.error(T_FILE_NOT_EXISTS % filename)
        self.shelf['filename'] = filename

        engines_list = engines.analyze(filename)
        engine = max(engines_list.iteritems(), key=operator.itemgetter(1))[0]
        self.shelf['engine'] = engine

    def build(self, pdf=True):
        os.chdir(TEAX_WORK_PATH + '/.teax/')
        engines.provide(self.shelf['filename'], self.shelf['engine'])
        for plugin in plugins.analyze(TEAX_WORK_PATH + '/.teax/'):
            plugins.provide(self.shelf['filename'], plugin)
            engines.provide(self.shelf['filename'], self.shelf['engine'])
            engines.provide(self.shelf['filename'], self.shelf['engine'])
        if pdf:
            shutil.copy(os.path.splitext(self.shelf['filename'])[0] + '.pdf', TEAX_WORK_PATH)
        os.chdir(TEAX_WORK_PATH)
