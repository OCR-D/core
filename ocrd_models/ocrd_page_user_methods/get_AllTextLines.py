def get_AllTextLines(self, region_order='document', textline_order='top-to-bottom'):
    """
    Return all the TextLine in the document

    Arguments:
        region_order ("document"|"reading-order"|"reading-order-only") Whether to
            return regions sorted by document order (``document``, default) or by
            reading order with regions not in the reading order at the end of the
            returned list (``reading-order``) or regions not in the reading order
            omitted (``reading-order-only``)
        textline_order ("top-to-bottom"|"bottom-to-top"|left-to-right"|"right-to-left")
            The order of text lines within a block (not currently used)
    """
    # TODO handle textLineOrder
    ret = []
    for reg in self.get_AllRegions(['Text'], order=region_order):
        ret += reg.get_TextLine()
    return ret

