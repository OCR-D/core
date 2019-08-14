"""
Base class for XML documents loaded from either content or filename.
"""
from os.path import exists
from lxml import etree as ET

from .constants import NAMESPACES
from .utils import xmllint_format


for curie in NAMESPACES:
    ET.register_namespace(curie, NAMESPACES[curie])

class OcrdXmlDocument():
    """
    Base class for XML documents loaded from either content or filename.
    """

    def __init__(self, filename=None, content=None):
        """
        Args:
            filename (string):
            content (string):
        """
        #  print(self, filename, content)
        if filename is None and content is None:
            raise Exception("Must pass 'filename' or 'content' to " + self.__class__.__name__)
        elif content:
            self._tree = ET.ElementTree(ET.XML(content, parser=ET.XMLParser(encoding='utf-8')))
        else:
            self._tree = ET.ElementTree()
            filename = filename.replace('file://', '')
            if not exists(filename):
                raise Exception('File does not exist: %s' % filename)
            self._tree.parse(filename)

    def to_xml(self, xmllint=False):
        """
        Serialize all properties as pretty-printed XML

        Args:
            xmllint (boolean): Format with ``xmllint`` in addition to pretty-printing
        """
        root = self._tree.getroot()
        ret = ET.tostring(ET.ElementTree(root), pretty_print=True, encoding='UTF-8')
        if xmllint:
            ret = xmllint_format(ret)
        return ret
