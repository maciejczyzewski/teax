# -*- coding: utf-8 -*-
"""teax system initialization"""

#== Engines

import teax.engines

from teax.system.engine import EngineFacade
engines = EngineFacade()

#== Plugins

import teax.plugins

from teax.system.plugin import PluginFacade
plugins = PluginFacade()
