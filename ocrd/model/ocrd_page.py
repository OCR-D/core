from io import StringIO

# pylint: disable=unused-import
from ocrd.model.ocrd_page_generateds import (
    parse,
    parseString,
    CoordsType,
    OrderedGroupType,
    ReadingOrderType,
    RegionRefIndexedType,
    TextEquivType,
    TextRegionType,
    TextLineType,
)
from ocrd.constants import PAGE_XML_EMPTY, NAMESPACES
from ocrd.model.ocrd_exif import OcrdExif

def to_xml(el):
    sio = StringIO()
    el.export(sio, 0, name_='PcGts', namespacedef_='xmlns:pc="%s"' % NAMESPACES['page'])
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + sio.getvalue()

def page_from_image(input_file):
    if input_file.local_filename is None:
        raise Exception("input_file must have 'local_filename' property")
    exif = OcrdExif.from_filename(input_file.local_filename)
    content = PAGE_XML_EMPTY.replace('<Page>', '<Page imageWidth="%d" imageHeight="%i" imageFilename="%s">' % (
        exif.width,
        exif.height,
        input_file.url
    ))
    return content

def from_file(input_file):
    """
    Create a new PAGE-XML from a METS file representing a PAGE-XML or an image.
    """
    #  print("PARSING PARSING '%s'" % input_file)
    if input_file.mimetype.startswith('image'):
        content = page_from_image(input_file)
        return parseString(content.encode('utf-8'), silence=True)
    elif input_file.mimetype == 'text/page+xml':
        return parse(input_file.local_filename, silence=True)
    else:
        raise Exception("Unsupported mimetype '%s'" % input_file.mimetype)
