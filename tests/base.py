# pylint: disable=unused-import

from os.path import dirname, realpath
from os import chdir, environ
from contextlib import contextmanager
import sys
import logging
import io
import collections
from unittest import TestCase as VanillaTestCase, skip, main as unittests_main
import pytest
from ocrd_utils import getLogger, initLogging, disableLogging
from ocrd_models import OcrdMets

from tests.assets import assets, copy_of_directory


sys.path.append(dirname(realpath(__file__)) + '/../ocrd')

@contextmanager
def ocrd_logging_enabled(**kwargs):
    disableLogging()
    for handler in logging.getLogger('').handlers:
        logging.getLogger('').removeHandler(handler)
    initLogging(force_reinit=True, **kwargs)
    yield
    disableLogging()
    for handler in logging.getLogger('').handlers:
        logging.getLogger('').removeHandler(handler)

def main(fn=None):
    if fn:
        sys.exit(pytest.main([fn]))
    else:
        unittests_main()


class TestCase(VanillaTestCase):

    def setUp(self):
        chdir(dirname(realpath(__file__)) + '/..')
        disableLogging()
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
        code = 0
        sys.argv[1:] = args # XXX necessary because sys.argv reflects pytest args not cli args
        try:
            cli.main(args=args)
        except SystemExit as e:
            code = e.code
        out, err = self.capture_out_err()
        return code, out, err

    def capture_out_err(self):
        return self.capfd.readouterr()

def create_ocrd_file_with_defaults(**kwargs):
    print('create_ocrd_file_with_defaults kwargs', kwargs)
    return create_ocrd_file('FOO', **{'ID': 'foo', **kwargs})

def create_ocrd_file(*args, **kwargs):
    mets = OcrdMets.empty_mets()
    return mets.add_file(*args, **kwargs)

#  import traceback
#  import warnings
#  def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
#      log = file if hasattr(file, 'write') else sys.stderr
#      traceback.print_stack(file=log)
#      log.write(warnings.formatwarning(message, category, filename, lineno, line))
#  warnings.showwarning = warn_with_traceback

class FIFOIO(io.TextIOBase):
    """
    https://stackoverflow.com/questions/37944111/python-rolling-log-to-a-variable
    Adapted from http://alanwsmith.com/capturing-python-log-output-in-a-variable
    """
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

@contextmanager
def capture_log(loggerName):
    log_capture_string = FIFOIO(1024)
    ch = logging.StreamHandler(log_capture_string)
    getLogger(loggerName).addHandler(ch)
    getLogger(loggerName).setLevel('DEBUG')
    try:
        yield log_capture_string
    finally:
        log_capture_string.close()

@contextmanager
def temp_env_var(k, v):
    v_before = environ.get(k, None)
    environ[k] = v
    yield
    if v_before is not None:
        environ[k] = v_before
    else:
        environ.pop(k)

