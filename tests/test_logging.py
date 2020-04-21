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
        with TemporaryDirectory() as tempdir:
            with pushd_popd(tempdir):
                with open('ocrd_logging.py', 'w') as f:
                    f.write('print("this is mighty dangerous")')
                initLogging()

class TestProfileLogging(TestCase):

    def testProcessorProfiling(self):
        log_capture_string = FIFOIO(256)
        ch = logging.StreamHandler(log_capture_string)
        ch.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(message)s'))
        getLogger('ocrd.process.profile').setLevel('DEBUG')
        getLogger('ocrd.process.profile').addHandler(ch)

        run_processor(DummyProcessor, resolver=Resolver(), mets_url=assets.url_of('SBB0000F29300010000/data/mets.xml'))

        log_contents = log_capture_string.getvalue()
        log_capture_string.close()
        # Check whether profile information has been logged. Dummy should finish in under 0.1s
        self.assertTrue(match(r'.*Executing processor "ocrd-test" took 0.\d+s.*', log_contents))

if __name__ == '__main__':
    main()
