import os
import logging
from tempfile import TemporaryDirectory

from tests.base import TestCase, main

from ocrd_utils.logging import (
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
        setOverrideLogLevel('INFO')


class TestLogging2(TestCase):

    def setUp(self):
        initLogging()

    def test_getLevelName(self):
        self.assertEqual(getLevelName('ERROR'), logging.ERROR)
        self.assertEqual(getLevelName('FATAL'), logging.ERROR)
        self.assertEqual(getLevelName('OFF'), logging.CRITICAL)

    def test_configfile(self):
        previous_dir = os.getcwd()
        with TemporaryDirectory() as tempdir:
            os.chdir(tempdir)
            with open('ocrd_logging.py', 'w') as f:
                f.write('print("this is mighty dangerous")')
            initLogging()
        os.chdir(previous_dir)

if __name__ == '__main__':
    main()
