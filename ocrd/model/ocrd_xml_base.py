from ocrd.constants import NAMESPACES

from lxml import etree as ET

for curie in NAMESPACES:
    ET.register_namespace(curie, NAMESPACES[curie])

# pylint: disable=no-member
class OcrdXmlBase(object):

    def __init__(self, filename=None, content=None):
        #  print(self, filename, content)
        if filename is None and content is None:
            raise Exception("Must pass 'filename' or 'content' to " + self.__class__.__name__)
        elif content:
            self._tree = ET.XML(content.encode('utf-8'), parser=ET.XMLParser(encoding='utf-8'))
        else:
            self._tree = ET.ElementTree() # pylint: disable=no-member
            self._tree.parse(filename)

    def to_xml(self):
        root = self._tree
        if hasattr(root, 'getroot'):
            root = root.getroot()
        return ET.tostring(ET.ElementTree(root), pretty_print=True)
