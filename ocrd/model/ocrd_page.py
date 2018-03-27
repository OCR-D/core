from ocrd.constants import (
    PAGE_XML_EMPTY,
    NAMESPACES,
    TAG_PAGE_READINGORDER,
    TAG_PAGE_REGIONREFINDEXED,
)
from ocrd.utils import getLogger

from .ocrd_xml_base import OcrdXmlDocument, ET
from .ocrd_page_textregion import OcrdPageTextRegion
from .ocrd_page_textline import OcrdPageTextLine

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

    # --------------------------------------------------
    # TextRegion
    # --------------------------------------------------

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

    # --------------------------------------------------
    # TextLine
    # --------------------------------------------------

    def add_textline(self, ID=None, coords=None):
        """
        Add a TextLine to the page.
        """
        return OcrdPageTextLine.create(self.page, ID=ID, coords=coords)

    def get_textline(self, n):
        """
        Get the n-th TextLine on the page.
        """
        return OcrdPageTextLine(self.page.find('page:TextLine[%i]' % (n + 1), NAMESPACES))

    def list_textlines(self):
        """
        List TextLine on page
        """
        return [OcrdPageTextLine(el) for el in self.page.findall('page:TextLine', NAMESPACES)]
