from ocrd.utils import getLogger
from ocrd.model import OcrdFile
from ocrd.model.ocrd_page import from_file, parse
from ocrd.constants import MIMETYPE_PAGE

from ocrd.model.ocrd_page_generateds import (
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

    def __init__(self, tag, ID, actual, expected):
        self.tag = tag
        self.ID = ID
        self.actual = actual
        self.expected = expected
        super(ConsistencyError, self).__init__("INCONSISTENCY in %s ID '%s': '%s' != '%s'" % (tag, ID, actual, expected))

class PageValidator(object):

    @staticmethod
    def validate_filename(filename, **kwargs):
        """
        Validates a PAGE file for consistency by filename

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        validator = PageValidator(parse(filename), **kwargs)
        return validator.validate()

    @staticmethod
    def validate_ocrd_page(page, **kwargs):
        """
        Validates an OcrdPage for consistency

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        validator = PageValidator(page, **kwargs)
        return validator.validate()


    @staticmethod
    def validate_ocrd_file(ocrd_file, **kwargs):
        """
        Validates an OcrdFile representing a PAGE doc for consistency

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        validator = PageValidator(from_file(ocrd_file), **kwargs)
        return validator.validate()

    def __init__(self, page, strictness='strict'):
        """
        Arguments:
            strictness (string): 'strict', 'fix' or 'off'
        """
        self.report = ValidationReport()
        self.page = page
        self.strictness = strictness

    def validate(self):
        """
        Do the validation / fixing.

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        if self.strictness == 'off':
            return self.report
        fix = self.strictness == 'fix'
        self.find_or_fix_inconsistencies(self.page, fix)
        return self.report

    def concatenate_index_1_text(self, node, concatenate_with):
        """
        Concatenate children of node according to https://ocr-d.github.io/page#consistency-of-text-results-on-different-levels
        """
        _, _, getter, concatenate_with = [x for x in _HIERARCHY if isinstance(node, x[0])][0]
        return concatenate_with.join([self.get_index_1_text(x) for x in getattr(node, getter)()]).strip()

    def get_index_1_text(self, node):
        """
        Get the most confident text results, either those with @index = 1 or the first text results or empty string.
        """
        textEquivs = node.get_TextEquiv()
        if not textEquivs:
            log.debug("No text results on %s %s", node, node.id)
            return ''
        else:
            if len(textEquivs) > 1:
                index1 = [x for x in textEquivs if x.index == 1]
                if index1:
                    return index1[0].get_Unicode().strip()
            return textEquivs[0].get_Unicode().strip()

    def set_index_1_text(self, node, text):
        """
        Set the most confident text results, either those with @index = 1, the first text results or add new one.
        """
        text = text.strip()
        textEquivs = node.get_TextEquiv()
        if not textEquivs:
            node.add_TextEquiv(TextEquivType(Unicode=text))
        else:
            if len(textEquivs) > 1:
                index1 = [x for x in textEquivs if x.index == 1]
                if index1:
                    index1[0].set_Unicode(text)
                    return
            textEquivs[0].set_Unicode(text)


    def find_or_fix_inconsistencies(self, node, fix=False):
        """
        Check whether the text results on an element is consistent with its child element text results.
        """
        if isinstance(node, PcGtsType):
            node = node.get_Page()
        elif isinstance(node, GlyphType):
            return []

        #  print("Checking %s" % node)
        #  print(_HIERARCHY)
        #  print(node)
        #  print([x for x in _HIERARCHY if isinstance(node, x[0])])

        errors = []
        _, tag, getter, concatenate_with = [x for x in _HIERARCHY if isinstance(node, x[0])][0]
        children_are_consistent = True
        if getter is not None:
            children = getattr(node, getter)()
            for child in children:
                child_errors = self.find_or_fix_inconsistencies(child, fix)
                if child_errors:
                    children_are_consistent = False
                    errors += child_errors
        if concatenate_with is not None:
            concatenated_children = self.concatenate_index_1_text(node, concatenate_with)
            text_results = self.get_index_1_text(node)
            #  print(text_results, concatenated_children)
            if concatenated_children != text_results:
                if fix:
                    if children_are_consistent:
                        self.set_index_1_text(node, concatenated_children)
                    else:
                        # TODO fix text results recursively
                        self.report.add_warning("Fixing inconsistencies recursively not implemented")
                else:
                    errors.append(ConsistencyError(tag, node.id, concatenate_with, text_results))
        self.report.errors += errors
        return errors
