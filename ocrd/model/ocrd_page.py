try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from datetime import datetime

# pylint: disable=unused-import
from ocrd.model.ocrd_page_generateds import (
    parse,
    parseString,

    AlternativeImageType,
    CoordsType,
    GlyphType,
    OrderedGroupType,
    PcGtsType,
    PageType,
    MetadataType,
    ReadingOrderType,
    RegionRefIndexedType,
    TextEquivType,
    TextRegionType,
    TextLineType,
    WordType,
)
from ocrd.constants import NAMESPACES, VERSION, MIMETYPE_PAGE
from ocrd.model.ocrd_exif import OcrdExif

def to_xml(el):
    sio = StringIO()
    el.export(sio, 0, name_='PcGts', namespacedef_='xmlns:pc="%s"' % NAMESPACES['page'])
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + sio.getvalue()

def page_from_image(input_file):
    if input_file.local_filename is None:
        raise Exception("input_file must have 'local_filename' property")
    exif = OcrdExif.from_filename(input_file.local_filename)
    now = datetime.now()
    return PcGtsType(
        Metadata=MetadataType(
            Creator="OCR-D/core %s" % VERSION,
            Created=now,
            LastChange=now
        ),
        Page=PageType(
            imageWidth=exif.width,
            imageHeight=exif.height,
            # XXX brittle
            imageFilename=input_file.url if input_file.url is not None else 'file://' + input_file.local_filename
        )
    )

def from_file(input_file):
    """
    Create a new PAGE-XML from a METS file representing a PAGE-XML or an image.
    """
    #  print("PARSING PARSING '%s'" % input_file)
    if input_file.mimetype.startswith('image'):
        return page_from_image(input_file)
    if input_file.mimetype == MIMETYPE_PAGE:
        return parse(input_file.local_filename, silence=True)
    raise Exception("Unsupported mimetype '%s'" % input_file.mimetype)
