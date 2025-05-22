"""
Constants for ocrd_models.
"""
from re import Pattern
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union
from ocrd_utils import resource_string

__all__ = [
    'IDENTIFIER_PRIORITY',
    'METS_XML_EMPTY',
    'NAMESPACES',
    'TAG_METS_AGENT',
    'TAG_METS_DIV',
    'TAG_METS_FILE',
    'TAG_METS_FILEGRP',
    'TAG_METS_FILESEC',
    'TAG_METS_FPTR',
    'TAG_METS_FLOCAT',
    'TAG_METS_METSHDR',
    'TAG_METS_NAME',
    'TAG_METS_NOTE',
    'TAG_METS_STRUCTMAP',
    'TAG_MODS_IDENTIFIER',
    'TAG_PAGE_ALTERNATIVEIMAGE',
    'TAG_PAGE_COORDS',
    'TAG_PAGE_READINGORDER',
    'TAG_PAGE_REGIONREFINDEXED',
    'TAG_PAGE_TEXTLINE',
    'TAG_PAGE_TEXTEQUIV',
    'TAG_PAGE_TEXTREGION',
    'METS_PAGE_DIV_ATTRIBUTE',
    'METS_STRUCT_DIV_ATTRIBUTE',
    'METS_DIV_ATTRIBUTE_ATOM_PATTERN',
    'METS_DIV_ATTRIBUTE_RANGE_PATTERN',
    'METS_DIV_ATTRIBUTE_REGEX_PATTERN',
    'PAGE_REGION_TYPES',
    'PAGE_ALTIMG_FEATURES',
]


IDENTIFIER_PRIORITY = ['purl', 'urn', 'doi', 'url']

METS_XML_EMPTY = resource_string(__package__, 'mets-empty.xml')

NAMESPACES = {
    'mets': "http://www.loc.gov/METS/",
    'mods': "http://www.loc.gov/mods/v3",
    'xlink': "http://www.w3.org/1999/xlink",
    'page': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15",
    'xsl': 'http://www.w3.org/1999/XSL/Transform#',
    'ocrd': 'https://ocr-d.de',
}

TAG_METS_AGENT            = '{%s}agent' % NAMESPACES['mets']
TAG_METS_DIV              = '{%s}div' % NAMESPACES['mets']
TAG_METS_FILE             = '{%s}file' % NAMESPACES['mets']
TAG_METS_FILEGRP          = '{%s}fileGrp' % NAMESPACES['mets']
TAG_METS_FILESEC          = '{%s}fileSec' % NAMESPACES['mets']
TAG_METS_FPTR             = '{%s}fptr' % NAMESPACES['mets']
TAG_METS_FLOCAT           = '{%s}FLocat' % NAMESPACES['mets']
TAG_METS_METSHDR          = '{%s}metsHdr' % NAMESPACES['mets']
TAG_METS_NAME             = '{%s}name' % NAMESPACES['mets']
TAG_METS_NOTE             = '{%s}note' % NAMESPACES['mets']
TAG_METS_STRUCTMAP        = '{%s}structMap' % NAMESPACES['mets']

TAG_MODS_IDENTIFIER       = '{%s}identifier' % NAMESPACES['mods']

TAG_PAGE_ALTERNATIVEIMAGE = '{%s}AlternativeImage' % NAMESPACES['page']
TAG_PAGE_COORDS           = '{%s}Coords' % NAMESPACES['page']
TAG_PAGE_READINGORDER     = '{%s}ReadingOrder' % NAMESPACES['page']
TAG_PAGE_REGIONREFINDEXED = '{%s}RegionRefIndexed' % NAMESPACES['page']
TAG_PAGE_TEXTLINE         = '{%s}TextLine' % NAMESPACES['page']
TAG_PAGE_TEXTEQUIV        = '{%s}TextEquiv' % NAMESPACES['page']
TAG_PAGE_TEXTREGION       = '{%s}TextRegion' % NAMESPACES['page']

PAGE_REGION_TYPES = [
    'Advert', 'Chart', 'Chem', 'Custom', 'Graphic', 'Image',
    'LineDrawing', 'Map', 'Maths', 'Music', 'Noise',
    'Separator', 'Table', 'Text', 'Unknown'
]

PAGE_ALTIMG_FEATURES = [
    'binarized',
    'grayscale_normalized',
    'despeckled',
    'cropped',
    'deskewed',
    'rotated-90',
    'rotated-180',
    'rotated-270',
    'dewarped',
    'clipped',
]


class METS_PAGE_DIV_ATTRIBUTE(Enum):
    ID = auto()
    ORDER = auto()
    ORDERLABEL = auto()
    LABEL = auto()
    CONTENTIDS = auto()

    @classmethod
    def names(cls):
        return [x.name for x in cls]
    @classmethod
    def type_prefix(cls):
        return "physical:"
    def prefix(self):
        return self.type_prefix() + self.name.lower() + ":"

class METS_STRUCT_DIV_ATTRIBUTE(Enum):
    ID = auto()
    DMDID = auto()
    TYPE = auto()
    LABEL = auto()

    @classmethod
    def names(cls):
        return [x.name for x in cls]
    @classmethod
    def type_prefix(cls):
        return "logical:"
    def prefix(self):
        return self.type_prefix() + self.name.lower() + ":"

@dataclass
class METS_DIV_ATTRIBUTE_PATTERN(ABC):
    # pattern
    expr: Any
    # pre-disambiguated with prefix syntax, or filled upon first match
    attr: List[Union[METS_PAGE_DIV_ATTRIBUTE, METS_STRUCT_DIV_ATTRIBUTE]] = field(
        default_factory=lambda: list(METS_PAGE_DIV_ATTRIBUTE) + list(METS_STRUCT_DIV_ATTRIBUTE))
    def attr_prefix(self):
        if self.attr == list(METS_PAGE_DIV_ATTRIBUTE) + list(METS_STRUCT_DIV_ATTRIBUTE):
            return ""
        if self.attr == list(METS_PAGE_DIV_ATTRIBUTE):
            return METS_PAGE_DIV_ATTRIBUTE.type_prefix()
        if self.attr == list(METS_STRUCT_DIV_ATTRIBUTE):
            return METS_STRUCT_DIV_ATTRIBUTE.type_prefix()
        assert len(self.attr) == 1, "unexpected type ambiguity: %s" % repr(self.attr)
        return self.attr[0].prefix()

    @abstractmethod
    def matches(self, input) -> bool:
        return

@dataclass
class METS_DIV_ATTRIBUTE_ATOM_PATTERN(METS_DIV_ATTRIBUTE_PATTERN):
    expr: str
    def __repr__(self):
        return "%s%s" % (self.attr_prefix(), self.expr)
    def matches(self, input):
        return input == self.expr

@dataclass
class METS_DIV_ATTRIBUTE_RANGE_PATTERN(METS_DIV_ATTRIBUTE_PATTERN):
    expr: List[str]
    start: str = field(init=False)
    stop: str = field(init=False)
    def __post_init__(self):
        self.start = self.expr[0]
        self.stop = self.expr[-1]
    def __repr__(self):
        return "%s%s..%s" % (self.attr_prefix(), self.start, self.stop)
    def matches(self, input):
        return input in self.expr

@dataclass
class METS_DIV_ATTRIBUTE_REGEX_PATTERN(METS_DIV_ATTRIBUTE_PATTERN):
    expr: Pattern
    def __repr__(self):
        return "%s//%s" % (self.attr_prefix(), self.expr.pattern)
    def matches(self, input):
        return bool(self.expr.fullmatch(input))
