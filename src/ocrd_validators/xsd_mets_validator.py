from .constants import XSD_METS_URL
from .xsd_validator import XsdValidator


class XsdMetsValidator(XsdValidator):
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
        return cls.instance(XSD_METS_URL)._validate(doc) # pylint: disable=protected-access
