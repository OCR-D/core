# pylint: disable=unused-import

from os.path import dirname, realpath
import sys
from unittest import TestCase, skip, main
import logging
import io
import collections

from .assets import assets, copy_of_directory

#  import traceback
#  import warnings
#  def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
#      log = file if hasattr(file, 'write') else sys.stderr
#      traceback.print_stack(file=log)
#      log.write(warnings.formatwarning(message, category, filename, lineno, line))
#  warnings.showwarning = warn_with_traceback

# https://stackoverflow.com/questions/37944111/python-rolling-log-to-a-variable
# Adapted from http://alanwsmith.com/capturing-python-log-output-in-a-variable

class FIFOIO(io.TextIOBase):
    def __init__(self, size, *args):
        self.maxsize = size
        io.TextIOBase.__init__(self, *args)
        self.deque = collections.deque()
    def getvalue(self):
        return ''.join(self.deque)
    def write(self, x):
        self.deque.append(x)
        self.shrink()
    def shrink(self):
        if self.maxsize is None:
            return
        size = sum(len(x) for x in self.deque)
        while size > self.maxsize:
            x = self.deque.popleft()
            size -= len(x)

sys.path.append(dirname(realpath(__file__)) + '/../ocrd')
