from ocrd.constants import (
    PAGE_XML_EMPTY,
    NAMESPACES,
    TAG_PAGE_COORDS,
    TAG_PAGE_READINGORDER,
    TAG_PAGE_REGIONREFINDEXED,
    TAG_PAGE_TEXTLINE,
    TAG_PAGE_TEXTEQUIV,
    TAG_PAGE_TEXTREGION,
)
from ocrd.utils import (
    getLogger,
    coordinate_string_from_xywh,
    xywh_from_coordinate_string
)

from .ocrd_xml_base import OcrdXmlDocument, ET
from .ocrd_page_textregion import OcrdPageTextRegion

log = getLogger('ocrd.model.ocrd_page')

class OcrdPage(OcrdXmlDocument):

    def __init__(self, *args, **kwargs):
        super(OcrdPage, self).__init__(*args, **kwargs)
        self._image_el = ET.Element('file')
        self._image_file = None

    @staticmethod
    def from_file(input_file):
        """
        Create a new PAGE-XML from a METS file representing a PAGE-XML or an image.
        """
        if input_file.mimetype.startswith('image'):
            content = PAGE_XML_EMPTY.replace('<Page>', '<Page imageFileName="%s">' % (input_file.url))
            return OcrdPage(content=content)
        elif input_file.mimetype == 'text/page+xml':
            return OcrdPage(filename=input_file.local_filename)

    def __str__(self):
        return '''
        <OcrdPage>
            imageFileName = %s
        </OcrdPage>
        ''' % (
            self._tree.find('page:Page', NAMESPACES).get('imageFileName')
        )

    @property
    def page(self):
        """
        The Page element
        """
        return self._tree.find('.//page:Page', NAMESPACES)

    @property
    def pcGtsId(self):
        """
        The pcGtsId of the root element
        """
        return self._tree.getroot().get('pcGtsId')

    @property
    def imageFileName(self):
        return self.page.get('imageFileName')

    @imageFileName.setter
    def imageFileName(self, v):
        self.page.set('imageFileName', v)

    @property
    def imageWidth(self):
        return self.page.get('imageWidth')

    @imageWidth.setter
    def imageWidth(self, v):
        self.page.set('imageWidth', v)

    @property
    def imageHeight(self):
        return self.page.get('imageHeight')

    @imageHeight.setter
    def imageHeight(self, v):
        self.page.set('imageHeight', v)

    @property
    def imageXResolution(self):
        return self.page.get('imageXResolution')

    @imageXResolution.setter
    def imageXResolution(self, v):
        self.page.set('imageXResolution', v)

    @property
    def imageYResolution(self):
        return self.page.get('imageYResolution')

    @imageYResolution.setter
    def imageYResolution(self, v):
        self.page.set('imageYResolution', v)

    @property
    def imageCompression(self):
        return self.page.get('imageCompression')

    @imageCompression.setter
    def imageCompression(self, v):
        self.page.set('imageCompression', v)

    @property
    def imagePhotometricInterpretation(self):
        return self.page.get('imagePhotometricInterpretation')

    @imagePhotometricInterpretation.setter
    def imagePhotometricInterpretation(self, v):
        self.page.set('imagePhotometricInterpretation', v)

    @property
    def imageResolutionUnit(self):
        return self.page.get('imageResolutionUnit')

    @imageResolutionUnit.setter
    def imageResolutionUnit(self, v):
        self.page.set('imageResolutionUnit', v)

    def add_reading_order_ref(self, region_ref, index):
        """
        Add the id of a region to the ReadingOrder
        """
        if self.page.find('.//page:ReadingOrder', NAMESPACES) is None:
            ET.SubElement(self.page, TAG_PAGE_READINGORDER)
        region_ref_indexed = ET.SubElement(self.page.find('.//page:ReadingOrder', NAMESPACES), TAG_PAGE_REGIONREFINDEXED)
        region_ref_indexed.set("regionRef", region_ref)
        region_ref_indexed.set("index", "%i" % index)

    def add_textregion(self, ID, coords):
        """
        Add a TextRegion
        """
        return OcrdPageTextRegion.create(self.page, ID=ID, coords=coords)

    def get_textregion(self, ID):
        """
        Get TextRegion with ID.
        """
        return OcrdPageTextRegion(self.page.find('.//*[id="%s"' % ID))

    def list_textregions(self):
        """
        List TextRegions as :py:mod:`OcrdPageTextRegion`
        """
        return [OcrdPageTextRegion(el) for el in self.page.findall('.//page:TextRegion', NAMESPACES)]

    def add_text_line(self, box, parent=None):
        """
        Add a TextLine. If parent is None, add TextLine to page. Otherwise
        choose parent by id.
        """
        parent = self.page if parent is None else self.page.find('.//*[@id="%s"]' % parent)
        line = ET.SubElement(parent, TAG_PAGE_TEXTLINE)
        coords = ET.SubElement(line, TAG_PAGE_COORDS)
        coords.set("points", coordinate_string_from_xywh(box))

    def number_of_text_lines(self, parent=None):
        """
        List number of lines for looping.
        """
        parent = self.page if parent is None else self.page.find('.//*[@id="%s"]' % parent)
        return len(parent.findall('.//page:TextLine', NAMESPACES))

    def get_text_line_coords(self, n, parent=None):
        """
        Find the n-th text line in page or region with id 'parent'.
        """
        parent = self.page if parent is None else self.page.find('.//*[@id="%s"]' % parent)
        points = parent.find('page:TextLine[%i]/page:Coords' % (n+1), NAMESPACES).get('points')
        return xywh_from_coordinate_string(points)

    def set_text_line_text_equiv(self, n, content, parent=None):
        """
        Set the TextEquiv text of the n-th line.
        """
        parent = self.page if parent is None else self.page.find('.//*[@id="%s"]' % parent)
        line = parent.find('page:TextLine[%i]' % (n+1), NAMESPACES)
        text_equiv = ET.SubElement(line, TAG_PAGE_TEXTEQUIV)
        text_equiv.text = content
