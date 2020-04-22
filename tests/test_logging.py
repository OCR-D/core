import logging
from re import match
from tempfile import TemporaryDirectory

from tests.base import TestCase, main, FIFOIO, assets
from tests.processor.test_processor import DummyProcessor
from ocrd import Resolver, run_processor

from ocrd_utils import (
    pushd_popd,
    getLevelName,
    setOverrideLogLevel,
    initLogging,
    getLogger,
    LOG_FORMAT,
    LOG_DATEFMT
)

class TestLogging(TestCase):

    def setUp(self):
        initLogging()

    def test_setOverrideLogLevel(self):
        rootLogger = logging.getLogger('')
        somelogger = getLogger('foo.bar')
        somelogger.setLevel(getLevelName('ERROR'))
        self.assertEqual(rootLogger.getEffectiveLevel(), logging.INFO)
        self.assertEqual(somelogger.getEffectiveLevel(), logging.ERROR)
        setOverrideLogLevel('ERROR')
        self.assertEqual(rootLogger.getEffectiveLevel(), logging.ERROR)
        self.assertEqual(somelogger.getEffectiveLevel(), logging.ERROR)
        notherlogger = getLogger('bar.foo')
        self.assertEqual(notherlogger.getEffectiveLevel(), logging.ERROR)
        setOverrideLogLevel('INFO')
        somelogger = getLogger('foo.bar')

    def test_getLevelName(self):
        self.assertEqual(getLevelName('ERROR'), logging.ERROR)
        self.assertEqual(getLevelName('FATAL'), logging.ERROR)
        self.assertEqual(getLevelName('OFF'), logging.CRITICAL)

    def test_logging_non_duplicate(self):
        """
        Verify that child loggers don't propagate a log message they handle
        """

        root_logger = logging.getLogger('')
        self.assertTrue(root_logger.handlers, 'root logger has at least 1 handler')

        parent_capture = FIFOIO(256)
        parent_handler = logging.StreamHandler(parent_capture)
        parent_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATEFMT))
        parent_logger = getLogger('foo')
        self.assertTrue(parent_logger.propagate, 'no handler on logger => propagate')
        parent_logger.addHandler(parent_handler)
        parent_logger = getLogger('foo')
        self.assertFalse(parent_logger.propagate, 'should not propagate because StreamHandler has been attached')

        child_capture = FIFOIO(256)
        child_handler = logging.StreamHandler(child_capture)
        child_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATEFMT))
        child_logger = getLogger('foo.bar')
        self.assertTrue(child_logger.propagate, 'no handler on logger => propagate')
        child_logger.addHandler(child_handler)
        child_logger = getLogger('foo.bar')
        self.assertFalse(child_logger.propagate, 'should not propagate because StreamHandler has been attached')

        child_logger.error('test')

        parent_output = parent_capture.getvalue()
        parent_capture.close()
        child_output = child_capture.getvalue()
        child_capture.close()
        # print('parent', parent_output)
        print('child', child_output)

        # self.assertEqual(parent_output, '', 'parent logger should not receive msg')
        # 0000-00-00 00:00:00,000.000 ERROR foo.bar - test\n
        self.assertTrue(match(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d(\.\d+)? ERROR foo.bar - test\n', child_output),
                'regex match the log entry format')

class TestLoggingConfiguration(TestCase):

    def test_tmpConfigfile(self):
        self.assertNotEqual(logging.getLogger('').getEffectiveLevel(), logging.NOTSET)
        with TemporaryDirectory() as tempdir:
            with pushd_popd(tempdir):
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
                        args=(sys.stdout,)
                        ''')
                # this will call logging.config.fileConfig with disable_existing_loggers=True,
                # so the defaults from the import-time initLogging should be invalided
                initLogging()
                # ensure log level is set from temporary config file
                self.assertEqual(logging.getLogger('').getEffectiveLevel(), logging.ERROR)

class TestProfileLogging(TestCase):

    def testProcessorProfiling(self):
        log_capture_string = FIFOIO(256)
        ch = logging.StreamHandler(log_capture_string)
        ch.setFormatter(logging.Formatter(LOG_FORMAT))
        getLogger('ocrd.process.profile').setLevel('DEBUG')
        getLogger('ocrd.process.profile').addHandler(ch)

        run_processor(DummyProcessor, resolver=Resolver(), mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'))

        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        # Check whether profile information has been logged. Dummy should finish in under 0.1s
        self.assertTrue(match(r'.*Executing processor "ocrd-test" took 0.\d+s.*', log_contents))

if __name__ == '__main__':
    main()
