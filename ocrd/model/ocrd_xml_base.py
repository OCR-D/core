from ocrd.constants import (
    NAMESPACES,
    TAG_PAGE_COORDS
)
from ocrd.utils import (
    xmllint_format,
    xywh_from_coordinate_string,
    coordinate_string_from_xywh
)

from lxml import etree as ET

for curie in NAMESPACES:
    ET.register_namespace(curie, NAMESPACES[curie])

class OcrdXmlFragment(object):

    def __init__(self, el):
        self.el = el

def get_coords(el):
    coords = el.find('page:Coords', NAMESPACES)
    if coords is not None:
        points = coords.get('points')
        return xywh_from_coordinate_string(points)

def set_coords(el, box):
    if box is not None:
        coords = el.find('page:Coords', NAMESPACES)
        if coords is None:
            coords = ET.SubElement(el, TAG_PAGE_COORDS)
        coords.set("points", coordinate_string_from_xywh(box))

class OcrdXmlDocument(object):

    def __init__(self, filename=None, content=None):
        #  print(self, filename, content)
        if filename is None and content is None:
            raise Exception("Must pass 'filename' or 'content' to " + self.__class__.__name__)
        elif content:
            self._tree = ET.ElementTree(ET.XML(content.encode('utf-8'), parser=ET.XMLParser(encoding='utf-8')))
        else:
            self._tree = ET.ElementTree()
            self._tree.parse(filename.replace('file://', ''))

    def to_xml(self, xmllint=False):
        root = self._tree
        if hasattr(root, 'getroot'):
            root = root.getroot()
        ret = ET.tostring(ET.ElementTree(root), pretty_print=True)
        if xmllint:
            ret = xmllint_format(ret)
        return ret
