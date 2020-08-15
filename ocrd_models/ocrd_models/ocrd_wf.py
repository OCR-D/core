from .constants import OCRD_WF_SHEBANG

class OcrdWf():

    def __init__(self, steps=None, assignments=None):
        self.steps = steps if steps else []
        self.assignments = assignments if assignments else []

    def __str__(self):
        ret = '%s\n' % OCRD_WF_SHEBANG
        for kv in self.assignments:
            k, v = kv
            ret += '%s=%s\n' % (k, v)
        for step in self.steps:
            ret += '%s\n' % str(step)
