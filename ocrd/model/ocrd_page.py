from ocrd.constants import PAGE_XML_EMPTY, NAMESPACES

from .ocrd_xml_base import OcrdXmlBase, ET

class OcrdPage(OcrdXmlBase):

    def __init__(self, *args, **kwargs):
        super(OcrdPage, self).__init__(*args, **kwargs)
        self._image_el = ET.Element('file') # pylint: disable=no-member
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
            return OcrdPage(filnename=input_file.local_filename)

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
        return self._tree.find('.//page:Page', NAMESPACES)

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
