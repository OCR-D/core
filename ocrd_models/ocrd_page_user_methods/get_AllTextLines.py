def get_AllTextLines(self, region_order='document', respect_textline_order=True):
    """
    Return all the TextLine in the document

    Arguments:
        region_order ("document"|"reading-order"|"reading-order-only"): Whether to \
            return regions sorted by document order (``document``, default) or by \
            reading order with regions not in the reading order at the end of the \
            returned list (``reading-order``) or regions not in the reading order \
            omitted (``reading-order-only``)
        respect_textline_order (boolean): Whether to respect `@textLineOrder` attribute

    Returns:
        a list of :py:class:`TextLineType`
    """
    # TODO handle textLineOrder according to https://github.com/PRImA-Research-Lab/PAGE-XML/issues/26
    ret = []
    for reg in self.get_AllRegions(['Text'], order=region_order):
        lines = reg.get_TextLine()
        if not respect_textline_order:
            ret += lines
        else:
            lo = reg.get_textLineOrder() or self.get_textLineOrder() or 'top-to-bottom'
            ret += lines if lo in ['top-to-bottom', 'left-to-right'] else list(reversed(lines))
    return ret

