"""
API to PAGE-XML, generated with generateDS from XML schema.
"""
from io import StringIO
from inspect import getmembers
from lxml import etree as ET

__all__ = [
    'parse',
    'parseEtree',
    'parseString',
    'OcrdPage',

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
    parseEtree,
    parseString,

    AdvertRegionType,
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

# add docstrings
parse.__doc__ = (
    """Parse a file, create the object tree, and export it.

    Arguments:
        inFileName (str) -- Path to the PAGE-XML file.
        print_warnings (boolean) -- If true, write parser \
                                    warnings to stderr.

    Returns:
        The root object in the tree.
    """
)

parseEtree.__doc__ = (
    """Parse a file, create the object tree, and export it. Return tree and mappings, too.

    Arguments:
        inFileName (str) -- Path to the PAGE-XML file.
        print_warnings (boolean) -- If true, write parser \
                                    warnings to stderr.

    Returns:
        A tuple of
         * The root object in the tree.
         * The full node tree.
         * A mapping from object IDs to tree nodes.
         * A reverse mapping from tree nodes to object IDs.
    """
)

# fix generated (malformed) docstrings
parseString.__doc__ = (
    """Parse a string, create the object tree, and export it.

    Arguments:
        inString (str) -- This XML fragment should not start \
                          with an XML declaration containing an encoding.

    Returns:
        The root object in the tree.
    """
)

class OcrdPage():
    """
    Proxy object for :py:class:`ocrd_models.PcGtsType` that also offers access
    to the underlying etree, element-node mapping and reverse mapping, too (cf.
    :py:func:`ocrd_models.ocrd_page.parseEtree`)
    """
    def __init__(
        self,
        pcgts : PcGtsType,
        etree : ET._Element,
        mapping : dict[str, ET._Element],
        revmap : dict[ET._Element, str],
    ):
        self._pcgts = pcgts
        self.etree = etree
        self.mapping = mapping
        self.revmap = revmap

    def __getattr__(self, name):
        return getattr(self._pcgts, name)

def to_xml(el, skip_declaration=False) -> str:
    """
    Serialize ``pc:PcGts`` document as string.
    """
    # XXX remove potential empty ReadingOrder
    if hasattr(el, 'prune_ReadingOrder'):
        el.prune_ReadingOrder()
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
    ret = sio.getvalue()
    if not skip_declaration:
        ret = '<?xml version="1.0" encoding="UTF-8"?>\n' + ret
    return ret
