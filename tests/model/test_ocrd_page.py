from tests.base import TestCase, main, assets

from ocrd_models.ocrd_page import (
    AlternativeImageType,
    PcGtsType,
    PageType,
    TextRegionType,
    TextLineType,
    WordType,
    GlyphType,

    parseString,
    to_xml
)
#  from ocrd.model_factory import page_from_file

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        with open(assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'), 'rb') as f:
            self.xml_as_str = f.read()
            self.pcgts = parseString(self.xml_as_str, silence=True)

    def test_to_xml(self):
        #  with open('/tmp/test.xml', 'w') as f:
        #      f.write(to_xml(self.pcgts))
        self.assertIn('</TextRegion', to_xml(self.pcgts))

    def test_pcGtsId(self):
        self.assertEqual(self.pcgts.pcGtsId, 'glyph-test')

    def test_imageFileName(self):
        #  print(self.pcgts.export(sys.stdout, 0))
        self.assertEqual(self.pcgts.get_Page().imageFilename, '00000259.sw.tif')
        self.pcgts.get_Page().imageFilename = 'foo'
        self.assertEqual(self.pcgts.get_Page().imageFilename, 'foo')

    def test_alternativeImage(self):
        pcgts = PcGtsType(pcGtsId="foo")
        self.assertEqual(pcgts.pcGtsId, 'foo')
        # Page/AlternativeImage
        page = PageType()
        pcgts.set_Page(page)
        page.add_AlternativeImage(AlternativeImageType())
        # TextRegion/AlternativeImage
        region = TextRegionType()
        page.add_TextRegion(region)
        region.add_AlternativeImage(AlternativeImageType())
        # TextLine/AlternativeImage
        line = TextLineType()
        region.add_TextLine(line)
        line.add_AlternativeImage(AlternativeImageType())
        # Word/AlternativeImage
        word = WordType()
        line.add_Word(word)
        word.add_AlternativeImage(AlternativeImageType())
        # Glyph/AlternativeImage
        glyph = GlyphType()
        word.add_Glyph(glyph)
        glyph.add_AlternativeImage(AlternativeImageType())


if __name__ == '__main__':
    main()
