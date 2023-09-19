import pytest
import logging
from re import match
from tempfile import TemporaryDirectory

from tests.base import main, FIFOIO, assets, ocrd_logging_enabled
from tests.data import DummyProcessor
from ocrd import Resolver, run_processor

from ocrd_utils import (
    pushd_popd,
    getLevelName,
    setOverrideLogLevel,
    getLogger,
    LOG_FORMAT,
    LOG_TIMEFMT
)

# "00:00:00.000 "
TIMEFMT_RE = r'\d\d:\d\d:\d\d\.(\d+)? '

def test_loglevel_inheritance():
    with ocrd_logging_enabled(builtin_only=True):
        ocrd_logger = logging.getLogger('ocrd')
        assert ocrd_logger.getEffectiveLevel() == logging.INFO
        some_logger = getLogger('ocrd.foo')
        assert some_logger.getEffectiveLevel() == logging.INFO
        setOverrideLogLevel('ERROR')
        assert ocrd_logger.getEffectiveLevel() == logging.ERROR
        assert some_logger.getEffectiveLevel() == logging.ERROR
        another_logger = getLogger('ocrd.bar')
        assert another_logger.getEffectiveLevel() == logging.ERROR

def test_getLevelName():
    assert getLevelName('ERROR') == logging.ERROR
    assert getLevelName('FATAL') == logging.ERROR
    assert getLevelName('OFF') == logging.CRITICAL

@pytest.mark.skip("""\
        This tests whether the message sent to one handler in the
        hierarchy will not also be sent to a handler of the parent logger.
        This is what Handler.propagate does and we do not mess with it any
        more, so the test is obsolete""")
def test_logging_really_non_duplicate():
    with ocrd_logging_enabled(builtin_only=True):
        ocrd_logger = getLogger('ocrd')
        parent_logger = getLogger('ocrd.a')
        child_logger = getLogger('ocrd.a.b')

        ocrd_capture = FIFOIO(256)
        ocrd_handler = logging.StreamHandler(ocrd_capture)
        ocrd_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
        ocrd_logger.addHandler(ocrd_handler)

        parent_capture = FIFOIO(256)
        parent_handler = logging.StreamHandler(parent_capture)
        parent_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
        parent_logger.addHandler(parent_handler)

        child_logger.error('test')

        ocrd_str = ocrd_capture.getvalue()
        parent_str = parent_capture.getvalue()
        print('ocrd_str=%s' % ocrd_str)
        print('parent_str=%s' % parent_str)

        assert ocrd_str.count('\n') == 0
        assert parent_str.count('\n') == 1

        # ocrd_logger.removeHandler(ocrd_handler) # remove stream handler so we actually see the output
        # ocrd_logger.info('ocrd_str=%s', ocrd_str)
        # ocrd_logger.info('parent_str=%s', parent_str)

@pytest.mark.skip("Skip for same reason as test_logging_non_duplicate")
def test_logging_non_duplicate():
    """
    Verify that child loggers don't propagate a log message they handle
    """
    with ocrd_logging_enabled():

        root_logger = logging.getLogger('')
        assert root_logger.handlers == 'root logger has at least 1 handler'

        parent_capture = FIFOIO(256)
        parent_handler = logging.StreamHandler(parent_capture)
        parent_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
        parent_logger = getLogger('foo')
        assert parent_logger.propagate, 'no handler on logger => propagate'
        parent_logger.addHandler(parent_handler)
        parent_logger = getLogger('foo')
        assert not parent_logger.propagate, 'should not propagate because StreamHandler has been attached'

        child_logger = getLogger('foo.bar')
        assert child_logger.propagate, 'no handler on logger => propagate'
        child_logger.setLevel('DEBUG')

        child_logger.error('first error')

        child_capture = FIFOIO(256)
        child_handler = logging.StreamHandler(child_capture)
        child_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))

        child_logger.debug('first debug')

        child_logger.addHandler(child_handler)
        child_logger = getLogger('foo.bar')
        assert child_logger.propagate == 'should not propagate because StreamHandler has been attached'

        child_logger.debug('second debug')
        child_logger.error('second error')

        parent_output = parent_capture.getvalue()
        parent_capture.close()
        child_output = child_capture.getvalue()
        child_capture.close()
        # print('parent', parent_output)
        # print('child', child_output)

        assert match(TIMEFMT_RE + 'ERROR foo.bar - first error\n', parent_output), 'parent received first error but not second error nor first debug'
        assert match("\n".join([
            TIMEFMT_RE + 'DEBUG foo.bar - second debug',
            TIMEFMT_RE + 'ERROR foo.bar - second error',
            ]), child_output), 'child received second error and debug but not first error and debug'

def testProcessorProfiling():
    with ocrd_logging_enabled(builtin_only=True):
        log_capture_string = FIFOIO(256)
        ch = logging.StreamHandler(log_capture_string)
        ch.setFormatter(logging.Formatter(LOG_FORMAT))
        getLogger('ocrd.process.profile').setLevel('DEBUG')
        getLogger('ocrd.process.profile').addHandler(ch)

        run_processor(DummyProcessor, resolver=Resolver(), mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'))

        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        # with open('/tmp/debug.log', 'w') as f:
        #     f.write(log_contents)
        # Check whether profile information has been logged. Dummy should finish in under 0.1s
        # print(log_contents)
        assert "Executing processor 'ocrd-test' took 0" in log_contents
        # assert match(r'.*Executing processor \'ocrd-test\' took 0.\d+s.*', log_contents)

def test_tmpConfigfile():
    assert logging.getLogger('ocrd').getEffectiveLevel() != logging.NOTSET
    with pushd_popd(tempdir=True) as tempdir:
        with open('ocrd_logging.conf', 'w') as f:
            # write logging configuration file (MWE)
            f.write('''
                [loggers]
                keys=root

                [handlers]
                keys=consoleHandler

                [formatters]
                keys=

                [logger_root]
                level=ERROR
                handlers=consoleHandler

                [handler_consoleHandler]
                class=StreamHandler
                formatter=
                args=(sys.stderr,)
                ''')
        with ocrd_logging_enabled(config_file_only=True):
            # ensure log level is set from temporary config file
            assert logging.getLogger('ocrd').getEffectiveLevel() == logging.ERROR

if __name__ == '__main__':
    main(__file__)
