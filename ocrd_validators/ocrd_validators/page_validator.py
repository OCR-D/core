"""
API for validating `OcrdPage <../ocrd_models/ocrd_models.ocrd_page.html>`_.
"""
import re
from shapely.geometry import Polygon, LineString
from shapely.validation import explain_validity

from ocrd_utils import getLogger, polygon_from_points, deprecated_alias
from ocrd_models.ocrd_page import parse
from ocrd_modelfactory import page_from_file

from ocrd_models.ocrd_page import (
    PcGtsType,
    PageType,
    TextRegionType,
    TextLineType,
    WordType,
    GlyphType,
    TextEquivType
)
from ocrd_models.ocrd_page_generateds import (
    RegionType,
    ReadingDirectionSimpleType,
    TextLineOrderSimpleType,
    RegionRefType,
    RegionRefIndexedType,
    OrderedGroupType,
    OrderedGroupIndexedType,
    UnorderedGroupType,
    UnorderedGroupIndexedType,
)
from .report import ValidationReport

log = getLogger('ocrd.page_validator')

_HIERARCHY = [
    # page can contain different types of regions
    (PageType,       'get_AdvertRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_ChartRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_ChemRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_CustomRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_GraphicRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_LineDrawingRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_MapRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_MathsRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_MusicRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_NoiseRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_SeparatorRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_TableRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_TextRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_UnknownRegion', None), # pylint: disable=bad-whitespace
    # all regions can be recursive
    (RegionType,     'get_AdvertRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_ChartRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_ChemRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_CustomRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_GraphicRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_LineDrawingRegion', None), # pylint: disable=bad-whitespace
    #(RegionType,     'get_MapRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_MathsRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_MusicRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_NoiseRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_SeparatorRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_TableRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_TextRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_UnknownRegion', None), # pylint: disable=bad-whitespace
    # only TextRegion can contain TextLine
    (TextRegionType, 'get_TextLine',   '\n'), # pylint: disable=bad-whitespace
    (TextLineType,   'get_Word',       ' '),  # pylint: disable=bad-whitespace
    (WordType,       'get_Glyph',      ''),   # pylint: disable=bad-whitespace
    (GlyphType,      None,             None), # pylint: disable=bad-whitespace
]

_ORDER = [
    (None, TextLineOrderSimpleType.BOTTOMTOTOP, ReadingDirectionSimpleType.RIGHTTOLEFT),
    (PageType,       'get_textLineOrder', 'get_readingDirection'), # pylint: disable=bad-whitespace
    (TextRegionType, 'get_textLineOrder', 'get_readingDirection'), # pylint: disable=bad-whitespace
    (TextLineType,   None,                'get_readingDirection'), # pylint: disable=bad-whitespace
    (WordType,       None,                'get_readingDirection'), # pylint: disable=bad-whitespace
]

# The following parameters control how tolerant we are with respect to
# polygon path self-validity and parent-child containment. We have to
# offer this, because most implementations, including PRImA itself,
# do _not_ offer pixel-precise correctness.
# How much may polygon paths deviate when simplifying them
# to avoid self-intersections?
POLY_TOLERANCE = 1.0
# How large a margin to increase parent polygons before
# checking their children are properly contained?
PARENT_SLACK = 1.5


class ConsistencyError(Exception):
    """
    Exception representing a consistency error in textual transcription across levels of a PAGE-XML.
    (Element text strings must be the concatenation of their children's text strings, joined by white space.)
    """

    def __init__(self, tag, ID, file_id, actual, expected):
        """
        Construct a new ConsistencyError.

        Arguments:
            tag (string): Level of the inconsistent element (parent)
            ID (string): ``ID`` of the inconsistent element (parent)
            file_id (string): ``mets:id`` of the PAGE file
            actual (string): Value of parent's TextEquiv[0]/Unicode
            expected (string): Concatenated values of children's
                               TextEquiv[0]/Unicode, joined by white-space
        """
        self.tag = tag
        self.ID = ID
        self.file_id = file_id
        self.actual = actual
        self.expected = expected
        super(ConsistencyError, self).__init__(
            "INCONSISTENCY in %s ID '%s' of file '%s': text results '%s' != concatenated '%s'" % (
                tag, ID, file_id, actual, expected))

class CoordinateConsistencyError(Exception):
    """
    Exception representing a consistency error in coordinate confinement across levels of a PAGE-XML.
    (Element coordinate polygons must be properly contained in their parents' coordinate polygons.)
    """

    def __init__(self, tag, ID, file_id, outer, inner):
        """
        Construct a new CoordinateConsistencyError.

        Arguments:
            tag (string): Level of the offending element (child)
            ID (string): ``ID`` of the offending element (child)
            file_id (string): ``mets:id`` of the PAGE file
            outer (string): Coordinate points of the parent
            inner (string): Coordinate points of the child
        """
        self.tag = tag
        self.ID = ID
        self.file_id = file_id
        self.outer = outer
        self.inner = inner
        super(CoordinateConsistencyError, self).__init__(
            "INCONSISTENCY in %s ID '%s' of '%s': coords '%s' not within parent coords '%s'" % (
                tag, ID, file_id, inner, outer))

class CoordinateValidityError(Exception):
    """
    Exception representing a validity error of an element's coordinates in PAGE-XML.
    (Element coordinate polygons must have at least 3 points, and must not
     self-intersect or be non-contiguous or be negative.)
    """

    def __init__(self, tag, ID, file_id, points, reason='unknown'):
        """
        Construct a new CoordinateValidityError.

        Arguments:
            tag (string): Level of the offending element (child)
            ID (string): ``ID`` of the offending element (child)
            points (string): Coordinate points
            reason (string): description of the problem
        """
        self.tag = tag
        self.ID = ID
        self.file_id = file_id
        self.points = points
        super(CoordinateValidityError, self).__init__(
            "INVALIDITY in %s ID '%s' of '%s': coords '%s' - %s" % (
                tag, ID, file_id, points, reason))

def compare_without_whitespace(a, b):
    """
    Compare two strings, ignoring all whitespace.
    """
    return re.sub('\\s+', '', a) == re.sub('\\s+', '', b)

def page_get_reading_order(ro, rogroup):
    """Add all elements from the given reading order group to the given dictionary.
    
    Given a dict ``ro`` from layout element IDs to ReadingOrder element objects,
    and an object ``rogroup`` with additional ReadingOrder element objects,
    add all references to the dict, traversing the group recursively.
    """
    if isinstance(rogroup, (OrderedGroupType, OrderedGroupIndexedType)):
        regionrefs = (rogroup.get_RegionRefIndexed() +
                      rogroup.get_OrderedGroupIndexed() +
                      rogroup.get_UnorderedGroupIndexed())
    if isinstance(rogroup, (UnorderedGroupType, UnorderedGroupIndexedType)):
        regionrefs = (rogroup.get_RegionRef() +
                      rogroup.get_OrderedGroup() +
                      rogroup.get_UnorderedGroup())
    for elem in regionrefs:
        ro[elem.get_regionRef()] = elem
        if not isinstance(elem, (RegionRefType, RegionRefIndexedType)):
            page_get_reading_order(ro, elem)

def make_poly(polygon_points):
    """Instantiate a Polygon from a list of point pairs, or return an error string"""
    if len(polygon_points) < 4:
        return 'has too few points'
    poly = Polygon(polygon_points)
    if POLY_TOLERANCE:
        poly = poly.simplify(POLY_TOLERANCE)
    if not poly.is_valid:
        return explain_validity(poly)
    elif poly.is_empty:
        return 'is empty'
    elif poly.bounds[0] < 0 or poly.bounds[1] < 0:
        return 'is negative'
    return poly

def make_line(line_points):
    """Instantiate a LineString from a list of point pairs, or return an error string"""
    if len(line_points) < 2:
        return 'has too few points'
    line = LineString(line_points)
    if not line.is_valid:
        return explain_validity(line)
    elif line.is_empty:
        return 'is empty'
    elif line.bounds[0] < 0 or line.bounds[1] < 0:
        return 'is negative'
    return line

@deprecated_alias(strictness='page_textequiv_consistency')
@deprecated_alias(strategy='page_textequiv_strategy')
def validate_consistency(node, page_textequiv_consistency, page_textequiv_strategy,
                         check_baseline, check_coords, report, file_id,
                         joinRelations=None, readingOrder=None,
                         textLineOrder=None, readingDirection=None):
    """
    Check whether the text results on an element is consistent with its child element text results,
    and whether the coordinates of an element are fully within its parent element coordinates.
    """
    if isinstance(node, PcGtsType):
        # top-level (start recursion)
        node_id = node.get_pcGtsId()
        node = node.get_Page() # has no .id
        if not readingOrder:
            readingOrder = dict()
        ro = node.get_ReadingOrder()
        if ro:
            page_get_reading_order(readingOrder, ro.get_OrderedGroup() or ro.get_UnorderedGroup())
        if not joinRelations:
            joinRelations = list()
        relations = node.get_Relations() # get RelationsType
        if relations:
            relations = relations.get_Relation() # get list of RelationType
        else:
            relations = []
        for relation in relations:
            if relation.get_type() == 'join': # ignore 'link' type here
                joinRelations.append((relation.get_SourceRegionRef().get_regionRef(),
                                      relation.get_TargetRegionRef().get_regionRef()))
    elif isinstance(node, GlyphType):
        # terminal level (end recursion)
        return True
    else:
        node_id = node.id
    tag = node.original_tagname_
    log.debug("Validating %s %s", tag, node_id)
    consistent = True
    if check_coords or check_baseline:
        if isinstance(node, PageType):
            parent = node.get_Border()
        else:
            parent = node
        if parent:
            parent_points = parent.get_Coords().points
            node_poly = make_poly(polygon_from_points(parent_points))
            if not isinstance(node_poly, Polygon):
                report.add_error(CoordinateValidityError(tag, node_id, file_id,
                                                         parent_points, node_poly))
                log.debug("Invalid coords of %s %s", tag, node_id)
                consistent = False
                node_poly = None # don't use in further comparisons
        else:
            node_poly = None
    for class_, getterLO, getterRD in _ORDER[1:]:
        if isinstance(node, class_):
            if getterLO:
                textLineOrder = getattr(node, getterLO)()
            if getterRD:
                readingDirection = getattr(node, getterRD)()
    for class_, getter, concatenate_with in _HIERARCHY:
        if not isinstance(node, class_):
            continue
        children = getattr(node, getter)()
        if (getter == 'get_TextRegion' and children and
            all(child.id in readingOrder for child in children) and
            isinstance(readingOrder[children[0].id].parent_object_,
                       (OrderedGroupType, OrderedGroupIndexedType))):
            children = sorted(children, key=lambda child:
                              readingOrder[child.id].index)
        elif ((getter == 'get_TextLine' and textLineOrder == _ORDER[0][1]) or
              (getter in ['get_Word', 'get_Glyph'] and readingDirection == _ORDER[0][2])):
            children = list(reversed(children))
        for child in children:
            consistent = (validate_consistency(child, page_textequiv_consistency, page_textequiv_strategy,
                                               check_baseline, check_coords,
                                               report, file_id,
                                               joinRelations, readingOrder,
                                               textLineOrder, readingDirection)
                          and consistent)
            if check_coords and node_poly:
                child_tag = child.original_tagname_
                child_points = child.get_Coords().points
                child_poly = make_poly(polygon_from_points(child_points))
                if not isinstance(child_poly, Polygon):
                    # report.add_error(CoordinateValidityError(child_tag, child.id, file_id, child_points))
                    # log.debug("Invalid coords of %s %s", child_tag, child.id)
                    # consistent = False
                    pass # already reported in recursive call above
                elif not child_poly.within(node_poly.buffer(PARENT_SLACK)):
                    # TODO: automatic repair?
                    report.add_error(CoordinateConsistencyError(child_tag, child.id, file_id,
                                                                parent_points, child_points))
                    log.debug("Inconsistent coords of %s %s", child_tag, child.id)
                    consistent = False
        if isinstance(node, TextLineType) and check_baseline and node.get_Baseline():
            baseline_points = node.get_Baseline().points
            baseline_line = make_line(polygon_from_points(baseline_points))
            if not isinstance(baseline_line, LineString):
                report.add_error(CoordinateValidityError("Baseline", node_id, file_id,
                                                         baseline_points, baseline_line))
                log.debug("Invalid coords of baseline in %s", node_id)
                consistent = False
            elif not baseline_line.within(node_poly.buffer(PARENT_SLACK)):
                report.add_error(CoordinateConsistencyError("Baseline", node_id, file_id,
                                                            parent_points, baseline_points))
                log.debug("Inconsistent coords of baseline in %s %s", tag, node_id)
                consistent = False
        if concatenate_with is not None and page_textequiv_consistency != 'off':
            # validate textual consistency of node with children
            concatenated = concatenate(children, concatenate_with, page_textequiv_strategy,
                                       joinRelations)
            text_results = get_text(node, page_textequiv_strategy)
            if concatenated and text_results and concatenated != text_results:
                consistent = False
                if page_textequiv_consistency == 'fix':
                    log.debug("Repaired text of %s %s", tag, node_id)
                    set_text(node, concatenated, page_textequiv_strategy)
                elif (page_textequiv_consistency == 'strict' # or 'lax' but...
                      or not compare_without_whitespace(concatenated, text_results)):
                    log.debug("Inconsistent text of %s %s", tag, node_id)
                    report.add_error(ConsistencyError(tag, node_id, file_id,
                                                      text_results, concatenated))
    return consistent

def concatenate(nodes, concatenate_with, page_textequiv_strategy, joins=None):
    """
    Concatenate nodes textually according to https://ocr-d.github.io/page#consistency-of-text-results-on-different-levels
    """
    if not nodes:
        return ''
    if not joins:
        joins = list()
    result = get_text(nodes[0], page_textequiv_strategy)
    for node, next_node in zip(nodes, nodes[1:]):
        if (node.id, next_node.id) not in joins:
            # TODO: also cover 2-level joins like word-word
            result += concatenate_with
        result += get_text(next_node, page_textequiv_strategy)
    return result.strip()

def get_text(node, page_textequiv_strategy='first'):
    """
    Get the first or most confident among text results (depending on ``page_textequiv_strategy``).
    For the strategy ``best``, return the string of the highest scoring result.
    For the strategy ``first``, return the string of the lowest indexed result.
    If there are no scores/indexes, use the first result.
    If there are no results, return the empty string.
    """
    textEquivs = node.get_TextEquiv()
    if not textEquivs:
        log.debug("No text results on %s %s", node, node.id)
        return ''
    elif page_textequiv_strategy == 'best':
        if len(textEquivs) > 1:
            textEquivsSorted = sorted([x for x in textEquivs if x.conf],
                                      # generateDS does not convert simpleType for attributes (yet?)
                                      key=lambda x: float(x.conf))
            if textEquivsSorted:
                return textEquivsSorted[-1].get_Unicode().strip()
        # fall back to first element
        return textEquivs[0].get_Unicode().strip()
    #elif page_textequiv_strategy == 'first':
    else:
        if len(textEquivs) > 1:
            textEquivsSorted = sorted([x for x in textEquivs if isinstance(x.index, int)],
                                      key=lambda x: x.index)
            if textEquivsSorted:
                return textEquivsSorted[0].get_Unicode().strip()
        # fall back to first element
        return textEquivs[0].get_Unicode().strip()

def set_text(node, text, page_textequiv_strategy):
    """
    Set the first or most confident among text results (depending on ``page_textequiv_strategy``).
    For the strategy ``best``, set the string of the highest scoring result.
    For the strategy ``first``, set the string of the lowest indexed result.
    If there are no scores/indexes, use the first result.
    If there are no results, add a new one.
    """
    text = text.strip()
    textEquivs = node.get_TextEquiv()
    if not textEquivs:
        node.add_TextEquiv(TextEquivType(Unicode=text)) # or index=0 ?
    elif page_textequiv_strategy == 'best':
        if len(textEquivs) > 1:
            textEquivsSorted = sorted([x for x in textEquivs if x.conf],
                                      # generateDS does not convert simpleType for attributes (yet?)
                                      key=lambda x: float(x.conf))
            if textEquivsSorted:
                textEquivsSorted[-1].set_Unicode(text)
                return
        # fall back to first element
        textEquivs[0].set_Unicode(text)
    #elif page_textequiv_strategy == 'first':
    else:
        if len(textEquivs) > 1:
            textEquivsSorted = sorted([x for x in textEquivs if isinstance(x.index, int)],
                                      key=lambda x: x.index)
            if textEquivsSorted:
                textEquivsSorted[0].set_Unicode(text)
                return
        # fall back to first element
        textEquivs[0].set_Unicode(text)

class PageValidator():
    """
    Validator for `OcrdPage <../ocrd_models/ocrd_models.ocrd_page.html>`.
    """

    @staticmethod
    @deprecated_alias(strictness='page_textequiv_consistency')
    @deprecated_alias(strategy='page_textequiv_strategy')
    def validate(filename=None, ocrd_page=None, ocrd_file=None,
                 page_textequiv_consistency='strict', page_textequiv_strategy='first',
                 check_baseline=True, check_coords=True):
        """
        Validates a PAGE file for consistency by filename, OcrdFile or passing OcrdPage directly.

        Arguments:
            filename (string): Path to PAGE
            ocrd_page (OcrdPage): OcrdPage instance
            ocrd_file (OcrdFile): OcrdFile instance wrapping OcrdPage
            page_textequiv_consistency (string): 'strict', 'lax', 'fix' or 'off'
            page_textequiv_strategy (string): Currently only 'first'
            check_baseline (bool): whether Baseline must be fully within TextLine/Coords
            check_coords (bool): whether *Region/TextLine/Word/Glyph must each be fully
                                 contained within Border/*Region/TextLine/Word, resp.

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        if ocrd_page:
            page = ocrd_page
            file_id = ocrd_page.get_pcGtsId()
        elif ocrd_file:
            page = page_from_file(ocrd_file)
            file_id = ocrd_file.ID
        elif filename:
            page = parse(filename, silence=True)
            file_id = filename
        else:
            raise Exception("At least one of ocrd_page, ocrd_file or filename must be set")
        if page_textequiv_strategy not in ('first'):
            raise Exception("page_textequiv_strategy %s not implemented" % page_textequiv_strategy)
        if page_textequiv_consistency not in ('strict', 'lax', 'fix', 'off'):
            raise Exception("page_textequiv_consistency level %s not implemented" % page_textequiv_consistency)
        report = ValidationReport()
        log.info("Validating input file '%s'", file_id)
        validate_consistency(page, page_textequiv_consistency, page_textequiv_strategy, check_baseline, check_coords, report, file_id)
        return report
