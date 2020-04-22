# pylint: disable=unused-import

from os.path import dirname, realpath
import sys
from unittest import TestCase as VanillaTestCase, skip, main
from .assets import assets, copy_of_directory
from ocrd_utils import (initLogging)

class TestCase(VanillaTestCase):

    def tearDown(self):
        initLogging()

#  import traceback
#  import warnings
#  def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
#      log = file if hasattr(file, 'write') else sys.stderr
#      traceback.print_stack(file=log)
#      log.write(warnings.formatwarning(message, category, filename, lineno, line))
#  warnings.showwarning = warn_with_traceback

sys.path.append(dirname(realpath(__file__)) + '/../ocrd')
