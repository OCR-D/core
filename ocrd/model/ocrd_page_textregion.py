from ocrd.utils import (
    coordinate_string_from_xywh,
    xywh_from_coordinate_string
)
from ocrd.constants import (
    NAMESPACES,
    TAG_PAGE_COORDS,
    TAG_PAGE_TEXTREGION,
)
from .ocrd_xml_base import OcrdXmlFragment, ET

class OcrdPageTextRegion(OcrdXmlFragment):

    @staticmethod
    def create(parent, ID=None, coords=None):
        el = ET.SubElement(parent, TAG_PAGE_TEXTREGION)
        ret = OcrdPageTextRegion(el)
        if ID is not None:
            ret.ID = ID
        if coords is not None:
            ret.coords = coords

    def __str__(self):
        return '[REGION ID="%s" coords="%s"]' % (self.ID, self.coords)

    @property
    def ID(self):
        return self.el.get('id')

    @ID.setter
    def ID(self, ID):
        if ID is not None:
            self.el.set('ID', ID)

    @property
    def coords(self):
        """
        Get the bounding box of a region
        """
        coords = self.el.find('page:Coords', NAMESPACES)
        if coords is not None:
            points = coords.get('points')
            return xywh_from_coordinate_string(points)

    @coords.setter
    def coords(self, box):
        """
        Set the bounding box of a region
        """
        if box is not None:
            coords = self.el.find('page:Coords', NAMESPACES)
            if coords is None:
                coords = ET.SubElement(self.el, TAG_PAGE_COORDS)
            coords.set("points", coordinate_string_from_xywh(box))
