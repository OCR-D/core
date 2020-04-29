"""
API to PAGE-XML, generated with generateDS from XML schema.
"""
from io import StringIO

__all__ = [
    'parse',
    'parseString',

    'AlternativeImageType',
    'CoordsType',
    'GlyphType',
    'ImageRegionType',
    'LabelType',
    'LabelsType',
    'MathsRegionType',
    'MetadataType',
    'MetadataItemType',
    'NoiseRegionType',
    'OrderedGroupType',
    'PageType',
    'PcGtsType',
    'ReadingOrderType',
    'RegionRefIndexedType',
    'SeparatorRegionType',
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
    ImageRegionType,
    LabelType,
    LabelsType,
    MathsRegionType,
    MetadataType,
    MetadataItemType,
    NoiseRegionType,
    OrderedGroupType,
    PageType,
    PcGtsType,
    ReadingOrderType,
    RegionRefIndexedType,
    SeparatorRegionType,
    TextEquivType,
    TextLineType,
    TextRegionType,
    TextStyleType,
    WordType,
)

from .constants import NAMESPACES

def to_xml(el):
    """
    Serialize ``pc:PcGts`` document
    """
    sio = StringIO()
    el.export(sio, 0, name_='PcGts',
            namespacedef_='xmlns:pc="%s"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="%s %s/pagecontent.xsd"' % (
                NAMESPACES['page'],
                NAMESPACES['page'],
                NAMESPACES['page']
            ))
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + sio.getvalue()
