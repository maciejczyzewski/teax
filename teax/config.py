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
    Class which holds the configuration values.

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

    All values used in command-line interface should be here.
    """

    # Environment:
    STORAGE = {}         #: Holds local & loaded variables
    FILENAME = ''        #: Where the configuration file is located

    # Temporaries:
    _INSTANCE = None     #: Last loaded instance of ConfigParser()

    def __init__(self, filename='teax.ini'):
        self.load(filename)  # Load local environment...

    def load(self, filename=''):
        """ Loads configuration file. """
        if os.path.isfile(filename):
            self.FILENAME = filename
            self._load_instance()
        # Load last instance...
        if self._INSTANCE:
            _variables = self._convert_to_dict(self._INSTANCE)
            self.STORAGE = self._merge_dicts(self.STORAGE, _variables)

    def save(self, filename, keys):
        cfgfile = open(filename, 'w')
        # If there is no instance...
        if not self._INSTANCE:
            self._INSTANCE = configparser.ConfigParser()
        # Lets create that config file for next time.
        for key in keys:
            section, keyword = self._parse_address(key)
            if section not in self._INSTANCE.sections():
                self._INSTANCE.add_section(section)
            # Write it permanently.
            self._INSTANCE.set(section, keyword, self.__getitem__(key))
        # Save to file.
        self._INSTANCE.write(cfgfile)
        cfgfile.close()

    def __getitem__(self, key):
        level = len(self._parse_address(key))
        if level == 2:
            # 2d-layer -> return Variable()
            section, keyword = self._parse_address(key)
            if section in self.STORAGE and \
               keyword in self.STORAGE[section]:
                return self.STORAGE[section][keyword]
            return None
        elif level == 1:
            # 1d-layer -> return Dict()
            if key in self.STORAGE:
                return self.STORAGE[key]
            return None
        else:
            # Return as map of dicts.
            return self.STORAGE

    def __setitem__(self, key, value):
        # Set variable (but not save in file).
        section, keyword = self._parse_address(key)
        if not section in self.STORAGE:
            self.STORAGE[section] = {}
        self.STORAGE[section][keyword] = value

    def _load_instance(self):
        # Use ConfigParser() to parser .ini files.
        try:
            self._INSTANCE = configparser.ConfigParser()
            self._INSTANCE.read(self.FILENAME)
        except:
            tty.warning(T_CONF_FILE_FAILURE)

    def _convert_to_dict(self, instance, _dict={}):
        # ConfigParser() instance to Dict()
        for section in instance.sections():
            _dict[section] = {}
            for key, val in instance.items(section):
                _dict[section][key] = val
        return _dict

    def _merge_dicts(self, left, right, path=[]):
        for key in right:
            # Merge b --> a (dicts in dicts)
            if key in left and isinstance(
                    left[key],
                    dict) and isinstance(
                    right[key],
                    dict):
                self._merge_dicts(left[key], right[key], path + [str(key)])
            else:
                left[key] = right[key]
        return left

    def _parse_address(self, string):
        if not string:
            return []
        return string.split('.')  # a.b.c --> [a][b][c]
