from ocrd.constants import (
    NAMESPACES,
    TAG_PAGE_TEXTEQUIV,
    TAG_PAGE_TEXTLINE
)

from .ocrd_xml_base import (
    OcrdXmlFragment,
    ET,
    get_coords,
    set_coords
)

class OcrdPageTextLine(OcrdXmlFragment):

    @staticmethod
    def create(parent, textequiv=None, ID=None, coords=None):
        el = ET.SubElement(parent, TAG_PAGE_TEXTLINE)
        ret = OcrdPageTextLine(el)
        if ID is not None:
            ret.ID = ID
        if coords is not None:
            ret.coords = coords
        if textequiv is not None:
            ret.textequiv = textequiv
        return ret

    def __str__(self):
        return '[TextLine ID="%s" coords="%s" textequiv="%s"]' % (self.ID, self.coords, self.textequiv)

    @property
    def ID(self):
        return self.el.get('id')

    @ID.setter
    def ID(self, ID):
        if ID is not None:
            self.el.set('ID', ID)

    # --------------------------------------------------
    # TextEquiv
    # --------------------------------------------------

    @property
    def textequiv(self):
        textequiv = self.el.find('page:TextEquiv', NAMESPACES)
        if textequiv:
            return textequiv.text

    @textequiv.setter
    def textequiv(self, content):
        """
        Set the TextEquiv of the TextLine.
        """
        textequiv = self.el.find('page:TextEquiv', NAMESPACES)
        if textequiv is None:
            textequiv = ET.SubElement(self.el, TAG_PAGE_TEXTEQUIV)
        textequiv.text = content

    # --------------------------------------------------
    # Coords
    # --------------------------------------------------

    @property
    def coords(self):
        """
        Get the bounding box of a TextLine
        """
        return get_coords(self.el)

    @coords.setter
    def coords(self, box):
        """
        Set the bounding box of a TextLine
        """
        set_coords(self.el, box)
