from io import StringIO

__all__ = [
    'parse',
    'parseString',

    'AlternativeImageType',
    'CoordsType',
    'GlyphType',
    'LabelType',
    'LabelsType',
    'MetadataType',
    'MetadataItemType',
    'OrderedGroupType',
    'PageType',
    'PcGtsType',
    'ReadingOrderType',
    'RegionRefIndexedType',
    'TextEquivType',
    'TextLineType',
    'TextStyleType',
    'TextRegionType',
    'WordType',

    'to_xml'
]

from .ocrd_page_generateds import (
    parse,
    parseString,

    AlternativeImageType,
    CoordsType,
    GlyphType,
    LabelType,
    LabelsType,
    MetadataType,
    MetadataItemType,
    OrderedGroupType,
    PageType,
    PcGtsType,
    ReadingOrderType,
    RegionRefIndexedType,
    TextEquivType,
    TextLineType,
    TextRegionType,
    TextStyleType,
    WordType,
)

from .constants import NAMESPACES

def to_xml(el):
    sio = StringIO()
    el.export(sio, 0, name_='PcGts', namespacedef_='xmlns:pc="%s"' % NAMESPACES['page'])
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + sio.getvalue()
