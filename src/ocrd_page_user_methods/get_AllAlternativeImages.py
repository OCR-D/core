def get_AllAlternativeImages(self, page=True, region=True, line=True, word=True, glyph=True):
    """
    Get all the ``pc:AlternativeImage`` in a document

    Arguments:
        page (boolean): Get images on ``pc:Page`` level
        region (boolean): Get images on ``pc:*Region`` level
        line (boolean): Get images on ``pc:TextLine`` level
        word (boolean): Get images on ``pc:Word`` level
        glyph (boolean): Get images on ``pc:Glyph`` level

    Returns:
        a list of :py:class:`AlternativeImageType`
    """
    ret = []
    if page:
        ret += self.get_AlternativeImage()
    for this_region in self.get_AllRegions(['Text']):
        if region:
            ret += this_region.get_AlternativeImage()
        for this_line in this_region.get_TextLine():
            if line:
                ret += this_line.get_AlternativeImage()
            for this_word in this_line.get_Word():
                if word:
                    ret += this_word.get_AlternativeImage()
                for this_glyph in this_word.get_Glyph():
                    if glyph:
                        ret += this_glyph.get_AlternativeImage()
    return ret

