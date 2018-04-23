
from test.base import TestCase, main, assets
import ocrd.model.ocrd_page as ocrd_page

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        with open(assets.url_of('page-with-glyphs.xml').replace('file://', ''), 'r') as f:
            self.xml = f.read()

    def test_pcGtsId(self):
        print(self.xml)
        p = ocrd_page.CreateFromDocument(self.xml)
        #  print(p)
        #  self.assertEqual(self.page.pcGtsId, '00000005')

    #  def test_imageFileName(self):
    #      self.assertTrue(self.page._tree.find('*[@imageFileName="%s"]'%'foo') is None)
    #      self.page.imageFileName = 'foo'
    #      self.assertEqual(self.page.imageFileName, 'foo')
    #      self.assertFalse(self.page._tree.find('*[@imageFileName="%s"]'%'foo') is None)

if __name__ == '__main__':
    main()
