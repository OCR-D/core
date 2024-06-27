from os.path import exists
from os import remove, getcwd
from time import sleep
from contextlib import ExitStack
from multiprocessing import Process, set_start_method
# necessary for macos
set_start_method("fork")

from ocrd import Resolver, Workspace, OcrdMetsServer
from ocrd.cli import process_cli
from ocrd_utils import pushd_popd

from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory

class TestCli(TestCase):

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
        self.assertTrue(exists('OCR-D-DUMMY'))

    def test_cli_process_mets_server(self):
        # stolen from test_mets_server.fixture_start_mets_server ...
        def _start_mets_server(*args, **kwargs):
            mets_server = OcrdMetsServer(*args, **kwargs)
            mets_server.startup()
        if exists('mets.sock'):
            remove('mets.sock')
        ws = Workspace(Resolver(), getcwd())
        p = Process(target=_start_mets_server, kwargs={'workspace': ws, 'url': 'mets.sock'})
        p.daemon = True
        p.start()
        sleep(1)  # sleep to start up server
        self.assertTrue(exists('mets.sock'))
        code, out, err = self.invoke_cli(process_cli, ['-U', 'mets.sock', 'dummy -I OCR-D-GT-PAGE -O OCR-D-DUMMY'])
        print(code, out, err)
        self.assertFalse(code)
        self.assertTrue(exists('OCR-D-DUMMY'))
        p.terminate()
        ws.reload_mets()
        self.assertIn('OCR-D-DUMMY', ws.mets.file_groups)

if __name__ == '__main__':
    main(__file__)
