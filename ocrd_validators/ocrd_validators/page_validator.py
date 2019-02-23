"""
API for validating `OcrdPage <../ocrd_models/ocrd_models.ocrd_page.html>`_.
"""
import re

from ocrd_utils import getLogger
from ocrd_models.ocrd_page import parse
from ocrd_modelfactory import page_from_file

from ocrd_models.ocrd_page import (
    PcGtsType,
    PageType,
    TextEquivType,
    TextRegionType,
    TextLineType,
    WordType,
    GlyphType,
)
from .report import ValidationReport

log = getLogger('ocrd.page_validator')

_HIERARCHY = [
    (PageType,       'Page',       'get_TextRegion', None), # pylint: disable=bad-whitespace
    (TextRegionType, 'TextRegion', 'get_TextLine',   '\n'), # pylint: disable=bad-whitespace
    (TextLineType,   'TextLine',   'get_Word',       ' '),  # pylint: disable=bad-whitespace
    (WordType,       'Word',       'get_Glyph',      ''),   # pylint: disable=bad-whitespace
    (GlyphType,      'Glyph',      None,             None), # pylint: disable=bad-whitespace
]

class ConsistencyError(Exception):
    """
    Exception representing a consistency error in transcription level of a PAGE-XML.
    """

    def __init__(self, tag, ID, actual, expected):
        """
        Construct a new ConsistencyError.

        Arguments:
            tag (string): Level of the inconsistent element
            ID (string): ``ID`` of the inconsistent element
            actual (string):
            expected (string):
        """
        self.tag = tag
        self.ID = ID
        self.actual = actual
        self.expected = expected
        super(ConsistencyError, self).__init__("INCONSISTENCY in %s ID '%s': text results '%s' != concatenated '%s'" % (tag, ID, actual, expected))

def compare_without_whitespace(a, b):
    """
    Compare two strings, ignoring all whitespace.
    """
    return re.sub('\\s+', '', a) == re.sub('\\s+', '', b)

def handle_inconsistencies(node, strictness, strategy, report):
    """
    Check whether the text results on an element is consistent with its child element text results.
    """
    if isinstance(node, PcGtsType):
        node = node.get_Page()
    elif isinstance(node, GlyphType):
        return report

    _, tag, getter, concatenate_with = [x for x in _HIERARCHY if isinstance(node, x[0])][0]
    children_are_consistent = True
    children = getattr(node, getter)()
    for child in children:
        errors_before = len(report.errors)
        handle_inconsistencies(child, strictness, strategy, report)
        if len(report.errors) > errors_before:
            children_are_consistent = False
    if concatenate_with is not None:
        concatenated_children = concatenate_children(node, concatenate_with, strategy)
        text_results = get_text(node, strategy)
        if concatenated_children and text_results and concatenated_children != text_results:
            if strictness == 'fix':
                set_text(node, concatenated_children, strategy)
                #  if children_are_consistent:
                #  else:
                #      # TODO fix text results recursively
                #      report.add_warning("Fixing inconsistencies recursively not implemented")
            elif strictness == 'lax':
                if not compare_without_whitespace(concatenated_children, text_results):
                    report.add_error(ConsistencyError(tag, node.id, text_results, concatenated_children))
            else:
                report.add_error(ConsistencyError(tag, node.id, text_results, concatenated_children))
    return report

def concatenate_children(node, concatenate_with, strategy):
    """
    Concatenate children of node according to https://ocr-d.github.io/page#consistency-of-text-results-on-different-levels
    """
    _, _, getter, concatenate_with = [x for x in _HIERARCHY if isinstance(node, x[0])][0]
    tokens = [get_text(x, strategy) for x in getattr(node, getter)()]
    return concatenate_with.join(tokens).strip()

def get_text(node, strategy):
    """
    Get the most confident text results, either those with @index = 1 or the first text results or empty string.
    """
    textEquivs = node.get_TextEquiv()
    if not textEquivs:
        log.debug("No text results on %s %s", node, node.id)
        return ''
    #  elif strategy == 'index1':
    else:
        if len(textEquivs) > 1:
            index1 = [x for x in textEquivs if x.index == 1]
            if index1:
                return index1[0].get_Unicode().strip()
        return textEquivs[0].get_Unicode().strip()

def set_text(node, text, strategy):
    """
    Set the most confident text results, either those with @index = 1, the first text results or add new one.
    """
    text = text.strip()
    textEquivs = node.get_TextEquiv()
    if not textEquivs:
        node.add_TextEquiv(TextEquivType(Unicode=text))
    #  elif strategy == 'index1':
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
    def validate(filename=None, ocrd_page=None, ocrd_file=None, strictness='strict', strategy='index1'):
        """
        Validates a PAGE file for consistency by filename, OcrdFile or passing OcrdPage directly.

        Arguments:
            filename (string): Path to PAGE
            ocrd_page (OcrdPage): OcrdPage instance
            ocrd_file (OcrdFile): OcrdFile instance wrapping OcrdPage
            strictness (string): 'strict', 'lax', 'fix' or 'off'
            strategy (string): Currently only 'index1'

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        if ocrd_page:
            validator = PageValidator(ocrd_page, strictness, strategy)
        elif ocrd_file:
            validator = PageValidator(page_from_file(ocrd_file), strictness, strategy)
        elif filename:
            validator = PageValidator(parse(filename, silence=True), strictness, strategy)
        else:
            raise Exception("At least one of ocrd_page, ocrd_file or filename must be set")
        return validator._validate() # pylint: disable=protected-access

    def __init__(self, page, strictness, strategy):
        """
        Arguments:
            page (OcrdPage): The OcrdPage to validate
        """
        if strategy not in ('index1'):
            raise Exception("Element selection strategy %s not implemented" % strategy)
        if strictness not in ('strict', 'lax', 'fix', 'off'):
            raise Exception("Strictness level %s not implemented" % strictness)
        self.report = ValidationReport()
        self.page = page
        self.strictness = strictness
        self.strategy = strategy

    def _validate(self):
        """
        Do the actual validation
        """
        if self.strictness == 'off':
            return self.report
        handle_inconsistencies(self.page, self.strictness, self.strategy, self.report)
        return self.report
