from __future__ import unicode_literals

from waves.settings import waves_settings

__all__ = ['AdaptorLoader']


class AdaptorLoader(object):
    adaptors_classes = waves_settings.ADAPTORS_CLASSES

    def get_adaptors(self):
        return sorted([adaptor_class() for adaptor_class in self.adaptors_classes])

    def load(self, clazz, **params):
        if params is None:
            params = {}
        return next((x(**params) for x in self.adaptors_classes if x == clazz), None)
