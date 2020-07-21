"""
Validating XML Schema
"""

from pathlib import Path
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
    _instances = {}

    @classmethod
    def instance(cls, schema_url):
        if schema_url in cls._instances:
            return cls._instances[schema_url]
        cls._instances[schema_url] = cls(schema_url)
        return cls._instances[schema_url]

    @classmethod
    def validate(cls, schema_url, doc):
        """
        Validate an XML document against a schema.

        Args:
            doc (etree.ElementTree|str|bytes):
            schema_url (str): URI of XML schema to validate against.
        """
        return cls.instance(schema_url)._validate(doc) # pylint: disable=protected-access

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
            doc (etree.ElementTree|str|bytes|pathlib.Path): the document. if etree: us as-is. if str/bytes: parse as XML string. If Path: read_text on it

        Returns: ValidationReport
        """
        report = ValidationReport()
        if isinstance(doc, Path):
            doc = ET.parse(str(doc))
        if isinstance(doc, (bytes, str)):
            doc = ET.fromstring(doc)
        try:
            self._xmlschema.assertValid(doc)
        except ET.DocumentInvalid as fail:
            for err in fail.error_log:  # pylint: disable=no-member
                report.add_error("Line %s: %s" % (err.line, err.message))
        return report
