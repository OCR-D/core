from test.base import TestCase, main, assets

from ocrd_models import OcrdFile

from ocrd_models.ocrd_page import (
    AlternativeImageType,
    PcGtsType,
    PageType,
    TextRegionType,
    TextLineType,
    WordType,
    GlyphType,

    parseString
)
#  from ocrd.model_factory import page_from_file

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        with open(assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS'), 'rb') as f:
            self.xml_as_str = f.read()
            self.pcgts = parseString(self.xml_as_str, silence=True)

    def test_from_file(self):
        f = OcrdFile(
            None,
            mimetype='image/tiff',
            local_filename=assets.path_to('kant_aufklaerung_1784/data/OCR-D-IMG/INPUT_0017')
        )
        self.assertEqual(f.mimetype, 'image/tiff')
        # TODO
        #  p = page_from_file(f)
        #  self.assertEqual(p.get_Page().imageWidth, 1457)

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
