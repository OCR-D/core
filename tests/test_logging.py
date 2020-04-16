import logging
from tempfile import TemporaryDirectory

from tests.base import TestCase, main

from ocrd_utils import (
    pushd_popd,
    getLevelName,
    setOverrideLogLevel,
    initLogging,
    getLogger
)

class TestLogging(TestCase):

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
        setOverrideLogLevel('INFO')


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
        

if __name__ == '__main__':
    main()
