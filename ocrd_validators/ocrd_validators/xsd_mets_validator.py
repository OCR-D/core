from .xsd_validator import XsdValidator
from .constants import XSD_METS_URL

class XsdMetsValidator(XsdValidator):
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
        return XsdMetsValidator()._validate(doc) # pylint: disable=protected-access

    def __init__(self):
        """
        Construct an XsdMetsValidator.
        """
        super().__init__(XSD_METS_URL)
