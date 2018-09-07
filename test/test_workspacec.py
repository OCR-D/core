# pylint: disable=protected-access
from shutil import rmtree
import os

from test.base import TestCase, assets, main

from ocrd.resolver import Resolver

class TestResolver(TestCase):

    def setUp(self):
        self.resolver = Resolver()

    def test_url_alias(self):
        tempdir = '/tmp/pyocrd-test-url-alias'
        if os.path.exists(tempdir):
            rmtree(tempdir)
        workspace = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/mets.xml'), directory=tempdir)
        self.assertEqual(workspace._url_aliases, {})


if __name__ == '__main__':
    main()
