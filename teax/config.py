# -*- coding: utf-8 -*-
"""teax configuration parser"""

import os

from teax import tty
from teax.messages import T_CONF_FILE_FAILURE

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class ConfigObject(object):
    """
    Config class for specifying teax specific optional items via a INI
    configuration file format. The main configuration class provides utilities
    for loading the configuration from disk and iterating across all the
    settings.

        >>> conf = ConfigObject('my_config.ini')
        >>> print conf['book']
        {u'author': u'MAC'}
        >>> conf['book.author'] = 'OMG'
        >>> conf['book.test'] = {'a': 1234, 'b': 4321}
        >>> print conf['book']
        {'test': {'a': 1234, 'b': 4321}, u'author': u'OMG'}
        >>> conf.load()
        >>> print conf['book']
        {'test': {'a': 1234, 'b': 4321}, u'author': u'MAC'}

    All values or options used in command-line interface should be here.
    Subclasses of the configuration specify defaults that can be updated via
    the configuration file.
    """
    # Environment:
    FILENAME = 'teax.ini'  #: Where the configuration file is located

    # Mode:
    M_LOAD_LOCALS = True   #: If positive loads the local environment

    def __init__(self, filename=FILENAME):
        self.__storage = {}
        self.__filename = ''
        self.__config_parser = None

        if self.M_LOAD_LOCALS:
            self.load(filename)

    def load(self, filename=''):
        """Load configuration file.
        Try to load local or last configuration environment. If none of them
        specified, it overwrites old values.
        """
        if os.path.isfile(filename):
            self.__filename = filename
            self.__load_instance()
        if self.__config_parser:
            data = self.__convert_to_dict(self.__config_parser)
            self.__storage = self.__merge_dicts(self.__storage, data)

    def save(self, filename, keys):
        """Save current configuration data to file.
        For safety reasons it writes to file only those values which will be
        indicated. It uses the current instance of config parser.
        """
        config_file = open(filename, 'w')
        if not self.__config_parser:
            self.__config_parser = configparser.ConfigParser()
        for key in keys:
            section, keyword = self.__parse_address(key)
            if section not in self.__config_parser.sections():
                self.__config_parser.add_section(section)
            self.__config_parser.set(section, keyword, self.__getitem__(key))
        self.__config_parser.write(config_file)
        config_file.close()

    def __getitem__(self, key):
        if not key:
            return self.__storage
        if len(self.__parse_address(key)) >= 2:
            section, keyword = self.__parse_address(key)
            if section in self.__storage and \
               keyword in self.__storage[section]:
                return self.__storage[section][keyword]
        elif key in self.__storage:
            return self.__storage[key]
        return None

    def __setitem__(self, key, value):
        section, keyword = self.__parse_address(key)
        if section not in self.__storage:
            self.__storage[section] = {}
        self.__storage[section][keyword] = value

    def __load_instance(self):
        try:
            self.__config_parser = configparser.ConfigParser()
            self.__config_parser.read(self.__filename)
        except:
            tty.warning(T_CONF_FILE_FAILURE)

    def __convert_to_dict(self, instance, data={}):
        for section in instance.sections():
            data[section] = {}
            for key, val in instance.items(section):
                data[section][key] = val
        return data

    def __merge_dicts(self, left, right, path=[]):
        for key in right:
            if key not in left:
                left[key] = right[key]
                continue
            if (type(left[key]) and type(right[key])) is dict:
                self.__merge_dicts(left[key], right[key], path + [str(key)])
            else:
                left[key] = right[key]
        return left

    def __parse_address(self, string):
        return filter(None, string.split('.'))
