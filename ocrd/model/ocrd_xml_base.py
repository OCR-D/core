from lxml import etree as ET

class OcrdXmlBase(object):

    def __init__(self, filename=None, content=None):

        if not filename and not content:
            raise Exception("Must pass 'filename' or 'content' to " + self.__class__.__name__)
        elif content:
            print(content)
            self._tree = ET.XML(content.encode('utf-8'), parser=ET.XMLParser(encoding='utf-8')) # pylint: disable=no-member
        else:
            self._tree = ET.ElementTree() # pylint: disable=no-member
            self._tree.parse(filename)
