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
from ocrd_models.ocrd_page_generateds import RegionType
from .report import ValidationReport

log = getLogger('ocrd.page_validator')

_HIERARCHY = [
    # page can contain different types of regions
    (PageType,       'get_AdvertRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_ChartRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_ChemRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_GraphicRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_GraphicRegion', None), # pylint: disable=bad-whitespace
    (PageType,       'get_LineDrawingRegion', None), # pylint: disable=bad-whitespace
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
    (RegionType,     'get_GraphicRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_GraphicRegion', None), # pylint: disable=bad-whitespace
    (RegionType,     'get_LineDrawingRegion', None), # pylint: disable=bad-whitespace
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

@deprecated_alias(strictness='page_textequiv_consistency')
@deprecated_alias(strategy='page_textequiv_strategy')
def validate_consistency(node, page_textequiv_consistency, page_textequiv_strategy, check_baseline, check_coords, report, file_id):
    """
    Check whether the text results on an element is consistent with its child element text results,
    and whether the coordinates of an element are fully within its parent element coordinates.
    """
    if isinstance(node, PcGtsType):
        # top-level (start recursion)
        node_id = node.get_pcGtsId()
        node = node.get_Page() # has no .id
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
            node_poly = Polygon(polygon_from_points(parent_points))
            reason = ''
            if not node_poly.is_valid:
                reason = explain_validity(node_poly)
            elif node_poly.is_empty:
                reason = 'is empty'
            elif node_poly.bounds[0] < 0 or node_poly.bounds[1] < 0:
                reason = 'is negative'
            elif node_poly.length < 4:
                reason = 'has too few points'
            if reason:
                report.add_error(CoordinateValidityError(tag, node_id, file_id, parent_points, reason))
                log.debug("Invalid coords of %s %s", tag, node_id)
                consistent = False
        else:
            node_poly = None
    for class_, getter, concatenate_with in _HIERARCHY:
        if not isinstance(node, class_):
            continue
        children = getattr(node, getter)()
        for child in children:
            consistent = (validate_consistency(child, page_textequiv_consistency, page_textequiv_strategy,
                                               check_baseline, check_coords,
                                               report, file_id)
                          and consistent)
            if check_coords and node_poly:
                child_tag = child.original_tagname_
                child_points = child.get_Coords().points
                child_poly = Polygon(polygon_from_points(child_points))
                if (not child_poly.is_valid
                    or child_poly.is_empty
                    or child_poly.bounds[0] < 0
                    or child_poly.bounds[1] < 0
                    or child_poly.length < 4):
                    # report.add_error(CoordinateValidityError(child_tag, child.id, file_id, child_points))
                    # log.debug("Invalid coords of %s %s", child_tag, child.id)
                    # consistent = False
                    pass # already reported in recursive call above
                elif not child_poly.within(node_poly):
                    # TODO: automatic repair?
                    report.add_error(CoordinateConsistencyError(tag, child.id, file_id,
                                                                parent_points, child_points))
                    log.debug("Inconsistent coords of %s %s", child_tag, child.id)
                    consistent = False
        if isinstance(node, TextLineType) and check_baseline and node.get_Baseline():
            baseline_points = node.get_Baseline().points
            baseline_line = LineString(polygon_from_points(baseline_points))
            reason = ''
            if not baseline_line.is_valid:
                reason = explain_validity(baseline_line)
            elif baseline_line.is_empty:
                reason = 'is empty'
            elif baseline_line.bounds[0] < 0 or baseline_line.bounds[1] < 0:
                reason = 'is negative'
            elif baseline_line.length < 2:
                reason = 'has too few points'
            if reason:
                report.add_error(CoordinateValidityError("Baseline", node_id, file_id, baseline_points, reason))
                log.debug("Invalid coords of baseline in %s", node_id)
                consistent = False
            elif not baseline_line.within(node_poly):
                report.add_error(CoordinateConsistencyError("Baseline", node_id, file_id,
                                                            parent_points, baseline_points))
                log.debug("Inconsistent coords of baseline in %s %s", tag, node_id)
                consistent = False
        if concatenate_with is not None and page_textequiv_consistency != 'off':
            # validate textual consistency of node with children
            concatenated = concatenate(children, concatenate_with, page_textequiv_strategy)
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

def concatenate(nodes, concatenate_with, page_textequiv_strategy):
    """
    Concatenate nodes textually according to https://ocr-d.github.io/page#consistency-of-text-results-on-different-levels
    """
    tokens = [get_text(node, page_textequiv_strategy) for node in nodes]
    return concatenate_with.join(tokens).strip()

def get_text(node, page_textequiv_strategy):
    """
    Get the most confident text results, either those with @index = 1 or the first text results or empty string.
    """
    textEquivs = node.get_TextEquiv()
    if not textEquivs:
        log.debug("No text results on %s %s", node, node.id)
        return ''
    #  elif page_textequiv_strategy == 'index1':
    else:
        if len(textEquivs) > 1:
            index1 = [x for x in textEquivs if x.index == 1]
            if index1:
                return index1[0].get_Unicode().strip()
        return textEquivs[0].get_Unicode().strip()

def set_text(node, text, page_textequiv_strategy):
    """
    Set the most confident text results, either those with @index = 1, the first text results or add new one.
    """
    text = text.strip()
    textEquivs = node.get_TextEquiv()
    if not textEquivs:
        node.add_TextEquiv(TextEquivType(Unicode=text))
    #  elif page_textequiv_strategy == 'index1':
    else:
        if len(textEquivs) > 1:
            index1 = [x for x in textEquivs if x.index == 1]
            if index1:
                index1[0].set_Unicode(text)
                return
        textEquivs[0].set_Unicode(text)

class PageValidator():
    """
    Validator for `OcrdPage <../ocrd_models/ocrd_models.ocrd_page.html>`.
    """

    @staticmethod
    @deprecated_alias(strictness='page_textequiv_consistency')
    @deprecated_alias(strategy='page_textequiv_strategy')
    def validate(filename=None, ocrd_page=None, ocrd_file=None,
                 page_textequiv_consistency='strict', page_textequiv_strategy='index1',
                 check_baseline=True, check_coords=True):
        """
        Validates a PAGE file for consistency by filename, OcrdFile or passing OcrdPage directly.

        Arguments:
            filename (string): Path to PAGE
            ocrd_page (OcrdPage): OcrdPage instance
            ocrd_file (OcrdFile): OcrdFile instance wrapping OcrdPage
            page_textequiv_consistency (string): 'strict', 'lax', 'fix' or 'off'
            page_textequiv_strategy (string): Currently only 'index1'
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
        if page_textequiv_strategy not in ('index1'):
            raise Exception("page_textequiv_strategy %s not implemented" % page_textequiv_strategy)
        if page_textequiv_consistency not in ('strict', 'lax', 'fix', 'off'):
            raise Exception("page_textequiv_consistency level %s not implemented" % page_textequiv_consistency)
        report = ValidationReport()
        log.info("Validating input file '%s'", file_id)
        validate_consistency(page, page_textequiv_consistency, page_textequiv_strategy, check_baseline, check_coords, report, file_id)
        return report
