"""
Validating XML Schema
"""

from lxml import etree as ET
from .report import ValidationReport
from .constants import XSD_PATHS

#
# -------------------------------------------------
#

class XsdValidator():
    """
    XML Schema validator.
    """

    @staticmethod
    def validate(schema_url, doc):
        """
        Validate an XML document against a schema.

        Args:
            doc (etree.ElementTree|str|bytes):
            schema_url (str): URI of XML schema to validate against.
        """
        return XsdValidator(schema_url)._validate(doc) # pylint: disable=protected-access

    def __init__(self, schema_url):
        """
        Construct an XsdValidator.

        Args:
            schema_url (str): URI of XML schema to validate against.
        """
        if schema_url not in XSD_PATHS:
            raise Exception('XML schema not bundled with OCR-D: %s' % schema_url)
        with open(XSD_PATHS[schema_url], 'r') as f:
            xmlschema_doc = ET.parse(f)
            self._xmlschema = ET.XMLSchema(xmlschema_doc)

    def _validate(self, doc):
        """
        Do the actual validation.

        Arguments:
            doc (etree.ElementTree|str|bytes):

        Returns: ValidationReport
        """
        report = ValidationReport()
        if isinstance(doc, (bytes, str)):
            doc = ET.fromstring(doc)
        try:
            self._xmlschema.assertValid(doc)
        except ET.DocumentInvalid as err:
            report.add_error("%s" % err)
        return report
