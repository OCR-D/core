from test.base import TestCase, main, assets
import ocrd.model.ocrd_file as ocrd_file
import ocrd.model.ocrd_page as ocrd_page

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        with open(assets.path_to('page-with-glyphs.xml'), 'rb') as f:
            self.xml_as_str = f.read()
            self.pcgts = ocrd_page.parseString(self.xml_as_str, silence=True)

    def test_from_file(self):
        f = ocrd_file.OcrdFile(
            None,
            mimetype='image/tif',
            local_filename=assets.path_to('kant_aufklaerung_1784/kant_aufklaerung_1784_0017.tif')
        )
        self.assertEqual(f.mimetype, 'image/tif')
        p = ocrd_page.from_file(f)
        self.assertEqual(p.get_Page().imageWidth, 1457)

    def test_pcGtsId(self):
        self.assertEqual(self.pcgts.pcGtsId, 'glyph-test')

    def test_imageFileName(self):
        #  print(self.pcgts.export(sys.stdout, 0))
        self.assertEqual(self.pcgts.get_Page().imageFilename, '00000259.sw.tif')
        self.pcgts.get_Page().imageFilename = 'foo'
        self.assertEqual(self.pcgts.get_Page().imageFilename, 'foo')

if __name__ == '__main__':
    main()
