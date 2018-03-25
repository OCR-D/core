#  from bs4 import BeautifulSoup
import xml.dom.minidom

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

    def to_xml_canonical(self):
#  <xsl:stylesheet version="1.0"
#    xmlns:xsl="http://www.w3.org/1999/XSL/Transform#">
#  </xsl:stylesheet>
        xslt_root = ET.XML('''\
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
      <xsl:template match="/*">
        <xsl:copy>
          <xsl:copy-of select="child::node()"/>
        </xsl:copy>
      </xsl:template>
    </xsl:stylesheet>
''')
        print(xslt_root)
#  ''', nsmap={'xsl': 'http://www.w3.org/1999/XSL/Transform#'})
        transform = ET.XSLT(xslt_root)
        result = transform(self._tree)
        return ET.tostring(result, pretty_print=True)

    def to_xml(self):
        #  return xml.dom.minidom.parseString(ET.tostring(self._tree, method='xml')).toprettyxml().encode('utf-8')
        #  return BeautifulSoup(ET.tostring(self._tree), 'xml').prettify().encode('utf-8')
        #  return self.to_xml_canonical()
        root = self._tree
        if hasattr(root, 'getroot'):
            root = root.getroot()
        #  output = StringIO()
        #  ET.ElementTree(root).write_c14n(output)
        #  return output.getvalue()
        #  print(md.parseString(ET.tostring(initializer.get_handle().page_trees[ID].getroot(), encoding='utf8', method='xml')).toprettyxml(indent="\t"))
        return ET.tostring(ET.ElementTree(root), pretty_print=True)
