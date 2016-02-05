# -*- coding: utf-8 -*-

import os
import time
import shutil

from teax import conf, tty, TEAX_REAL_PATH, TEAX_WORK_PATH
from teax.messages import T_TEMPLATE_NOT_EXISTS, T_DIRECTORY_EXISTS, \
    T_CREATING_TEMPLATE, T_USING_TEMPLATE


class TemplateObject(object):
    # Environment:
    PATH = ''            #: Where the template is located
    BASENAME = ''        #: Base name of template/structure

    def __init__(self, template):
        self.BASENAME = template.lower()
        self.PATH = TEAX_REAL_PATH + '/templates/' + self.BASENAME

        if not os.path.exists(self.PATH):
            tty.errn(T_TEMPLATE_NOT_EXISTS % self.BASENAME)

        tty.note(T_USING_TEMPLATE % self.BASENAME)

    def save(self, path):
        _local_path = TEAX_WORK_PATH + '/' + path

        if os.path.exists(_local_path):
            timestamp = str(int(time.time()))
            _local_path += '-' + timestamp
            tty.warn(T_DIRECTORY_EXISTS % timestamp)

        shutil.copytree(self.PATH, _local_path)

        tty.note(T_CREATING_TEMPLATE % path)

        _conf_file = TEAX_WORK_PATH + '/' + path + '/' + 'teax.ini'

        conf.save(_conf_file, [
            'general.title',
            'general.authors',
            'general.keywords'
        ])
