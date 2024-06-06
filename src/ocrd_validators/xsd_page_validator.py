from .xsd_validator import XsdValidator
from .constants import XSD_PAGE_URL

class XsdPageValidator(XsdValidator):
    """
    XML Schema validator.
    """

    @classmethod
    def validate(cls, doc):  # pylint: disable=arguments-differ
        """
        Validate an XML document against a schema

        Args:
            doc (etree.ElementTree|str|bytes):
        """
        return cls.instance(XSD_PAGE_URL)._validate(doc) # pylint: disable=protected-access
