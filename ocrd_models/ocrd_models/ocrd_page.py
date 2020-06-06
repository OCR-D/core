"""
API to PAGE-XML, generated with generateDS from XML schema.
"""
from io import StringIO

__all__ = [
    'parse',
    'parseString',

    "AdvertRegionType",
    "AlternativeImageType",
    "BaselineType",
    "BorderType",
    "ChartRegionType",
    "ChemRegionType",
    "CoordsType",
    "CustomRegionType",
    "GlyphType",
    "GraphemeBaseType",
    "GraphemeGroupType",
    "GraphemeType",
    "GraphemesType",
    "GraphicRegionType",
    "GridPointsType",
    "GridType",
    "ImageRegionType",
    "LabelType",
    "LabelsType",
    "LayerType",
    "LayersType",
    "LineDrawingRegionType",
    "MapRegionType",
    "MathsRegionType",
    "MetadataItemType",
    "MetadataType",
    "MusicRegionType",
    "NoiseRegionType",
    "NonPrintingCharType",
    "OrderedGroupIndexedType",
    "OrderedGroupType",
    "PageType",
    "PcGtsType",
    "PrintSpaceType",
    "ReadingOrderType",
    "RegionRefIndexedType",
    "RegionRefType",
    "RegionType",
    "RelationType",
    "RelationsType",
    "RolesType",
    "SeparatorRegionType",
    "TableCellRoleType",
    "TableRegionType",
    "TextEquivType",
    "TextLineType",
    "TextRegionType",
    "TextStyleType",
    "UnknownRegionType",
    "UnorderedGroupIndexedType",
    "UnorderedGroupType",
    "UserAttributeType",
    "UserDefinedType",
    "WordType",

    'to_xml'
]

from .ocrd_page_generateds import (
    parse,
    parseString,

    AlternativeImageType,
    BaselineType,
    BorderType,
    ChartRegionType,
    ChemRegionType,
    CoordsType,
    CustomRegionType,
    GlyphType,
    GraphemeBaseType,
    GraphemeGroupType,
    GraphemeType,
    GraphemesType,
    GraphicRegionType,
    GridPointsType,
    GridType,
    ImageRegionType,
    LabelType,
    LabelsType,
    LayerType,
    LayersType,
    LineDrawingRegionType,
    MapRegionType,
    MathsRegionType,
    MetadataItemType,
    MetadataType,
    MusicRegionType,
    NoiseRegionType,
    NonPrintingCharType,
    OrderedGroupIndexedType,
    OrderedGroupType,
    PageType,
    PcGtsType,
    PrintSpaceType,
    ReadingOrderType,
    RegionRefIndexedType,
    RegionRefType,
    RegionType,
    RelationType,
    RelationsType,
    RolesType,
    SeparatorRegionType,
    TableCellRoleType,
    TableRegionType,
    TextEquivType,
    TextLineType,
    TextRegionType,
    TextStyleType,
    UnknownRegionType,
    UnorderedGroupIndexedType,
    UnorderedGroupType,
    UserAttributeType,
    UserDefinedType,
    WordType
)

from .constants import NAMESPACES

def to_xml(el):
    """
    Serialize ``pc:PcGts`` document
    """
    sio = StringIO()
    el.export(
            outfile=sio,
            level=0,
            name_='PcGts',
            namespaceprefix_='pc:',
            namespacedef_='xmlns:pc="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="%s %s/pagecontent.xsd"' % (
                NAMESPACES['page'],
                NAMESPACES['page'],
                NAMESPACES['page']
            ))
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + sio.getvalue()
