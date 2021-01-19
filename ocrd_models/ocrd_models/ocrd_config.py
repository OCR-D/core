"""
Configuration file
"""
import json

DEFAULT_CONFIG = {
    'resource_location': 'virtualenv'
}

class OcrdConfig():

    __slots__ = DEFAULT_CONFIG.keys()

    def __str__(self):
        return 'OcrdConfig %s' % json.dumps(self.__dict__)

    def dump(self):
        ret = {}
        for k in DEFAULT_CONFIG.keys():
            ret[k] = getattr(self, k)
        return ret

    def __init__(self, obj):
        for k, v in obj.items():
            setattr(self, k, v)
