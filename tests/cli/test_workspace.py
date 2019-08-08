from os.path import join
#  from shutil import copyfile
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from tests.base import TestCase, main # pylint: disable=import-error, no-name-in-module

from ocrd_utils.logging import initLogging
from ocrd.cli.workspace import workspace_cli
from ocrd.resolver import Resolver

class TestCli(TestCase):


    def setUp(self):
        self.maxDiff = None
        self.resolver = Resolver()
        initLogging()
        self.runner = CliRunner()

    def test_add(self):
        """
        Ensure that `ocrd workspace add` does the right thing
        """
        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        content = 'x'
        mimetype = 'image/tiff'
        local_filename = join(file_grp, 'foo.xml')

        mets_api = None
        mets_cli = None

        with TemporaryDirectory() as tempdir:
            ws_api = self.resolver.workspace_from_nothing(directory=tempdir)
            ws_api.add_file(
                file_grp,
                ID=ID,
                content=content,
                pageId=page_id,
                mimetype=mimetype,
                local_filename=local_filename
            )
            ws_api.save_mets()
            mets_api = ws_api.mets.to_xml().decode('utf8')

        with TemporaryDirectory() as tempdir:
            ws_api = self.resolver.workspace_from_nothing(directory=tempdir)
            content_file = join(tempdir, 'testfile')
            with open(content_file, 'w') as f:
                f.write(content)
                result = self.runner.invoke(workspace_cli, [
                    '-d', tempdir,
                    'add',
                    '--file-grp', file_grp,
                    '--page-id', page_id,
                    '--file-id', ID,
                    '--mimetype', mimetype,
                    content_file
                ])
                #  print(result)
                self.assertEqual(result.exit_code, 0)
            with open(join(tempdir, 'mets.xml')) as f:
                mets_cli = f.read()
            #  print(mets_api)
            #  print(mets_cli)
            #  self.assertEqual(mets_api, mets_cli)
        #      print(result.output)


if __name__ == '__main__':
    main()
