# -*- coding: utf-8 -*-

from teax.messages import T_UNKNOWN_ADAPTER_NAME

class EngineObject:
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
    def match(cls, filename, points=0):
        return points


class EngineFacade:
    adapters = {}

    def __init__(self):
        pass  # Availability check? FIXME

    def analyze(self, filename):
        engines = {}
        for name, adapter in self.adapters.iteritems():
            engines[name] = adapter.match(filename)
        return engines

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
