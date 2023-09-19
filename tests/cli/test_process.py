from ocrd.cli import process_cli
from ocrd_utils import pushd_popd, disableLogging

from tests.base import CapturingTestCase as TestCase, main, assets, copy_of_directory, ocrd_logging_enabled

class TestLogCli(TestCase):

    def test_cli_process_smoke(self):
        with ocrd_logging_enabled():
            # only called for the side effect of disableLogging after yield
            pass
        with copy_of_directory(assets.path_to('kant_aufklaerung_1784/data')) as wsdir:
            with pushd_popd(wsdir):
                with self.assertRaisesRegex(Exception, "Executable not found in PATH: ocrd-foo"):
                    self.invoke_cli(process_cli, ['foo'])

if __name__ == '__main__':
    main(__file__)
