from ocrd.constants import PAGE_XML_EMPTY, NAMESPACES

from .ocrd_xml_base import OcrdXmlBase

class OcrdPage(OcrdXmlBase):

    @staticmethod
    def from_mets_file(mets_file):
        """
        Create a new PAGE-XML from a METS file representing an image.
        """
        content = PAGE_XML_EMPTY.replace('<Page>', '<Page imageFileName="%s">' % (mets_file.url))
        return OcrdPage(content=content)

    def __str__(self):
        return '''
        <OcrdPage>
            imageFileName = %s
        </OcrdPage>
        ''' % (
            self._tree.find('page:Page', NAMESPACES).get('imageFileName')
        )
