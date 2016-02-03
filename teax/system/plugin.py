# -*- coding: utf-8 -*-

from teax.messages import T_UNKNOWN_ADAPTER_NAME

class PluginObject:
    """
    Reference interface for adapter classes;
    inheritance is not necessary.
    """

    parseable_extensions = set()

    def __init__(self, filename):
        self.filename = filename

    def start(self):
        raise NotImplementedError

    @classmethod
    def is_active(cls, path):
        return False


class PluginFacade:
    adapters = {}

    def __init__(self):
        pass  # Availability check? FIXME

    def analyze(self, path):
        plugins = []
        for name, adapter in self.adapters.iteritems():
            if adapter.is_active(path):
                plugins.append(name)
        return plugins

    def provide(self, filename, name):
        try:
            adapter_cls = self.adapters[name]
        except KeyError:
            tty.error(T_UNKNOWN_ADAPTER_NAME % name)

        adapter = adapter_cls(filename)
        adapter.start()
        return adapter

    @classmethod
    def register(cls, adapter):
        cls.adapters[adapter.__name__] = adapter
