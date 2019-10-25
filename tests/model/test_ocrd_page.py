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
    parse,
    to_xml
)

simple_page = """\
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15/pagecontent.xsd">
    <Metadata>
        <Creator>OCR-D</Creator>
        <Created>2016-09-20T11:09:27.041+02:00</Created>
        <LastChange>2018-04-25T17:44:49.605+01:00</LastChange>
    </Metadata>
    <Page
        imageFilename="https://github.com/OCR-D/assets/raw/master/data/kant_aufklaerung_1784/data/OCR-D-IMG/INPUT_0017.tif"
        imageWidth="1457"
        imageHeight="2083"
        type="content">
        <TextRegion type="heading" id="r_1_1" custom="readingOrder {index:0;} structure {type:heading;}">
            <Coords points="113,365 919,365 919,439 113,439"/>
            <TextLine id="tl_1" primaryLanguage="German" custom="readingOrder {index:0;} textStyle {offset:0; length:26;fontFamily:Arial; fontSize:17.0; bold:true;}">
                <Coords points="114,366 918,366 918,438 114,438"/>
                <Baseline points="114,429 918,429"/>
                <Word id="w_w1aab1b1b2b1b1ab1" language="German" custom="readingOrder {index:0;} textStyle {offset:0; length:11;fontFamily:Arial; fontSize:17.0; bold:true;}">
                    <Coords points="114,368 442,368 442,437 114,437"/>
                    <TextEquiv conf="1">
                        <Unicode>Berliniſche</Unicode>
                    </TextEquiv>
                </Word>
            </TextLine>
        </TextRegion>
    </Page>
</PcGts>
"""

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        with open(assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS.xml'), 'rb') as f:
            self.xml_as_str = f.read()
            self.pcgts = parseString(self.xml_as_str, silence=True)

    def test_to_xml(self):
        #  with open('/tmp/test.xml', 'w') as f:
            #  f.write(to_xml(self.pcgts))
        self.assertIn(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd"', to_xml(self.pcgts)[:1000])
        self.assertIn('</pc:TextRegion', to_xml(self.pcgts))

    def test_issue_269(self):
        """
        @conf is parsed as str but should be float
        https://github.com/OCR-D/core/issues/269
        """
        # GIGO
        self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].set_conf(1.0)
        self.assertEqual(type(self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].get_conf()), float)
        self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].set_conf('1.0')
        self.assertEqual(type(self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].get_conf()), str)
        # test with parseString that @conf in TextEquiv won't throw an error
        parseString(simple_page, silence=True)
        #  self.assertTrue(True)

    def test_pcGtsId(self):
        self.assertEqual(self.pcgts.pcGtsId, 'glyph-test')

    def test_delete_region(self):
        pcgts = parseString(simple_page, silence=True)
        self.assertEqual(len(pcgts.get_Page().get_TextRegion()), 1)
        del pcgts.get_Page().get_TextRegion()[0]
        self.assertEqual(len(pcgts.get_Page().get_TextRegion()), 0)

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
