# pylint: disable=unused-import

from os.path import dirname, realpath
from os import chdir
import sys
import logging
import io
import collections
from unittest import TestCase as VanillaTestCase, skip, main as unittests_main
import pytest
from ocrd_utils import initLogging

from tests.assets import assets, copy_of_directory


def main(fn=None):
    if fn:
        sys.exit(pytest.main([fn]))
    else:
        unittests_main()


class TestCase(VanillaTestCase):

    @classmethod
    def setUpClass(cls):
        chdir(dirname(realpath(__file__)) + '/..')

    def tearDown(self):
        initLogging()

class CapturingTestCase(TestCase):
    """
    A TestCase that needs to capture stderr/stdout and invoke click CLI.
    """

    @pytest.fixture(autouse=True)
    def _setup_pytest_capfd(self, capfd):
        self.capfd = capfd

    def invoke_cli(self, cli, args):
        """
        Substitution for click.CliRunner.invooke that works together nicely
        with unittests/pytest capturing stdout/stderr.
        """
        self.capture_out_err()  # XXX snapshot just before executing the CLI
        try:
            cli.main(args=args)
        except SystemExit as e:
            out, err = self.capture_out_err()
            return e.code, out, err

    def capture_out_err(self):
        return self.capfd.readouterr()

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
