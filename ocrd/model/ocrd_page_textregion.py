from ocrd.constants import (
    NAMESPACES,
    TAG_PAGE_TEXTREGION,
)
from ocrd.model.ocrd_page_textline import OcrdPageTextLine
from .ocrd_xml_base import (
    OcrdXmlFragment,
    ET,
    get_coords,
    set_coords,
)

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
        return get_coords(self.el)

    @coords.setter
    def coords(self, box):
        """
        Set the bounding box of a region
        """
        set_coords(self.el, box)

    # --------------------------------------------------
    # TextLine
    # --------------------------------------------------

    def add_textline(self, textequiv=None, ID=None, coords=None):
        """
        Add a TextLine to the TextRegion.
        """
        return OcrdPageTextLine.create(self.el, textequiv=textequiv, ID=ID, coords=coords)

    def get_textline(self, n):
        """
        Get the n-th TextLine on the TextRegion.
        """
        return OcrdPageTextLine(self.el.find('page:TextLine[%i]' % (n + 1), NAMESPACES))

    def list_textlines(self):
        """
        List TextLine on TextRegion.
        """
        return [OcrdPageTextLine(el) for el in self.el.findall('page:TextLine', NAMESPACES)]
