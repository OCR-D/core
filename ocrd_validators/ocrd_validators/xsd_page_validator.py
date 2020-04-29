from .xsd_validator import XsdValidator
from .constants import XSD_PAGE_URL

class XsdPageValidator(XsdValidator):
    """
    XML Schema validator.
    """

    @staticmethod
    def validate(doc):  # pylint: disable=arguments-differ
        """
        Validate an XML document against a schema

        Args:
            doc (etree.ElementTree|str|bytes):
        """
        return XsdPageValidator()._validate(doc) # pylint: disable=protected-access

    def __init__(self):
        """
        Construct an XsdPageValidator.
        """
        super().__init__(XSD_PAGE_URL)
