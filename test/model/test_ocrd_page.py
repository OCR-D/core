from test.base import TestCase, main
from test.assets import METS_HEROLD_PAGE_5
from ocrd.model import OcrdPage

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        self.page = OcrdPage(filename=METS_HEROLD_PAGE_5.replace('file://', ''))

    def test_pcGtsId(self):
        self.assertEquals(self.page.pcGtsId, '00000005')

    def test_imageFileName(self):
        self.assertTrue(self.page._tree.find('*[@imageFileName="%s"]'%'foo') is None)
        self.page.imageFileName = 'foo'
        self.assertEquals(self.page.imageFileName, 'foo')
        self.assertFalse(self.page._tree.find('*[@imageFileName="%s"]'%'foo') is None)

if __name__ == '__main__':
    main()
