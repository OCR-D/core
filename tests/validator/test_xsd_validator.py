# pylint: disable=protected-access

from pathlib import Path
from tempfile import TemporaryDirectory

from tests.base import TestCase, main, assets
from ocrd import Resolver
from ocrd_models.constants import METS_XML_EMPTY
from ocrd_validators import XsdValidator, XsdMetsValidator, XsdPageValidator
from ocrd_validators.constants import XSD_METS_URL, XSD_PAGE_URL
from tests.model.test_ocrd_page import simple_page

class TestXsdValidator(TestCase):

    def setUp(self):
        super().setUp()
        self.resolver = Resolver()
        self.ws = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))

    def test_constructor(self):
        with self.assertRaisesRegex(Exception, 'schema not bundled'):
            XsdValidator('foo')
        XsdValidator(XSD_METS_URL)

    def test_mets_empty(self):
        with TemporaryDirectory() as tempdir:
            mets_path = Path(tempdir, 'mets.xml')
            mets_path.write_bytes(METS_XML_EMPTY)
            report = XsdMetsValidator.validate(mets_path)
            self.assertEqual(len(report.errors), 2)
            self.assertEqual(report.errors[0],
                    "Line 3: Element '{http://www.loc.gov/METS/}metsHdr', attribute 'CREATEDATE': '{{ NOW }}' is not a valid value of the atomic type 'xs:dateTime'.")
            self.assertEqual(report.errors[1],
                    "Line 18: Element '{http://www.loc.gov/METS/}fileSec': Missing child element(s). Expected is ( {http://www.loc.gov/METS/}fileGrp ).")
            self.assertFalse(report.is_valid)

    def test_validate_simple_protected_str(self):
        val = XsdValidator(XSD_METS_URL)
        report = val._validate(self.ws.mets.to_xml())
        self.assertTrue(report.is_valid)

    def test_validate_simple_protected_doc(self):
        val = XsdValidator(XSD_METS_URL)
        report = val._validate(self.ws.mets._tree)
        self.assertTrue(report.is_valid)

    def test_validate_simple_static_doc(self):
        report = XsdValidator.validate(XSD_METS_URL, self.ws.mets._tree)
        self.assertTrue(report.is_valid)

class TestXsdPageValidator(TestCase):

    def test_validate_page_simple_static_doc(self):
        report = XsdPageValidator.validate(simple_page)
        self.assertTrue(report.is_valid)

if __name__ == '__main__':
    main(__file__)
