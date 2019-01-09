try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


__all__ = [
    'parse',
    'parseString',

    'AlternativeImageType',
    'CoordsType',
    'GlyphType',
    'OrderedGroupType',
    'PcGtsType',
    'PageType',
    'MetadataType',
    'ReadingOrderType',
    'RegionRefIndexedType',
    'TextEquivType',
    'TextRegionType',
    'TextLineType',
    'WordType',

    'to_xml'
]

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
from ocrd.constants import NAMESPACES

def to_xml(el):
    sio = StringIO()
    el.export(sio, 0, name_='PcGts', namespacedef_='xmlns:pc="%s"' % NAMESPACES['page'])
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + sio.getvalue()
