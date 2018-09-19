import logging
from test.base import TestCase, main

from ocrd.logging import (
    getLevelName,
    setOverrideLogLevel,
)

class TestLogging(TestCase):

    #  def runTest(self):

    def test_getLevelName(self):
        self.assertEqual(getLevelName('ERROR'), logging.ERROR)
        self.assertEqual(getLevelName('FATAL'), logging.ERROR)
        self.assertEqual(getLevelName('OFF'), logging.CRITICAL)

    def test_setOverrideLogLevel(self):
        rootLogger = logging.getLogger('')
        somelogger = logging.getLogger('foo.bar')
        somelogger.setLevel(getLevelName('INFO'))
        self.assertEqual(somelogger.getEffectiveLevel(), logging.INFO)
        setOverrideLogLevel('ERROR')
        self.assertEqual(rootLogger.getEffectiveLevel(), logging.ERROR)
        self.assertEqual(somelogger.getEffectiveLevel(), logging.ERROR)
        notherlogger = logging.getLogger('bar.foo')
        self.assertEqual(notherlogger.getEffectiveLevel(), logging.ERROR)

if __name__ == '__main__':
    main()
