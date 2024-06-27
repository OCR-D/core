from contextlib import ExitStack

from ocrd.cli import process_cli
from ocrd_utils import pushd_popd, disableLogging

from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory

class TestLogCli(TestCase):

    def setUp(self):
        super().setUp()
        # make sure we get an isolated temporary copy of the testdata each time
        # as long as we are not using pytest but unittest, we need to manage contexts
        # (enterContext is only supported starting with py311)
        with ExitStack() as stack:
            self.workdir = stack.enter_context(copy_of_directory(assets.path_to('kant_aufklaerung_1784/data')))
            stack.enter_context(pushd_popd(self.workdir))
            self.addCleanup(stack.pop_all().close)

    def test_cli_process_smoke(self):
        with self.assertRaisesRegex(Exception, "Executable not found in PATH: ocrd-foo"):
            self.invoke_cli(process_cli, ['foo'])

    def test_cli_process_dummy(self):
        code, out, err = self.invoke_cli(process_cli, ['dummy -I OCR-D-GT-PAGE -O OCR-D-DUMMY'])
        print(code, out, err)
        self.assertFalse(code)

if __name__ == '__main__':
    main(__file__)
