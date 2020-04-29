# pylint: disable=protected-access

from tests.base import TestCase, main, assets
from ocrd import Resolver
from ocrd_validators import XsdValidator, XsdMetsValidator, XsdPageValidator
from ocrd_validators.constants import XSD_METS_URL, XSD_PAGE_URL
from tests.model.test_ocrd_page import simple_page

class TestXsdValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.ws = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))

    def test_constructor(self):
        with self.assertRaisesRegex(Exception, 'schema not bundled'):
            XsdValidator('foo')
        XsdValidator(XSD_METS_URL)

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

# class TestXsdMetsValidator(TestXsdValidator):

#     def test_validate_mets_simple_protected_doc(self):
#         val = XsdMetsValidator()
#         report = val._validate(self.ws.mets._tree)
#         self.assertTrue(report.is_valid)

#     def test_validate_mets_simple_static_doc(self):
#         report = XsdMetsValidator.validate(self.ws.mets._tree)
#         self.assertTrue(report.is_valid)

class TestXsdPageValidator(TestCase):

    def setUp(self):
        self.resolver = Resolver()
        self.ws = self.resolver.workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'))

    def test_validate_page_simple_protected_doc(self):
        val = XsdPageValidator()
        report = val._validate(simple_page)
        print(report.errors)
        self.assertTrue(report.is_valid)

    def test_validate_page_simple_static_doc(self):
        report = XsdPageValidator.validate(simple_page)
        print(report.errors)
        self.assertTrue(report.is_valid)

if __name__ == '__main__':
    main()
