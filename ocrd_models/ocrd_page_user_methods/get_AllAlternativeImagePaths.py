def get_AllAlternativeImagePaths(self, page=True, region=True, line=True, word=True, glyph=True):
    """
    Get all the ``pc:AlternativeImage/@filename`` paths referenced in the PAGE-XML document.

    Arguments:
        page (boolean): Get images on ``pc:Page`` level
        region (boolean): Get images on ``pc:*Region`` level
        line (boolean): Get images on ``pc:TextLine`` level
        word (boolean): Get images on ``pc:Word`` level
        glyph (boolean): Get images on ``pc:Glyph`` level

    Returns:
        a list of image filename strings
    """
    from .constants import NAMESPACES, PAGE_REGION_TYPES # pylint: disable=relative-beyond-top-level,import-outside-toplevel
    from io import StringIO  # pylint: disable=import-outside-toplevel
    ret = []
    # XXX Since we're only interested in the **paths** of the images,
    # export, parse and xpath are less convoluted than traversing
    # the generateDS API. Quite possibly not as efficient as could be.
    sio = StringIO()
    self.export(
            outfile=sio,
            level=0,
            name_='PcGts',
            namespaceprefix_='pc:',
            namespacedef_='xmlns:pc="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="%s %s/pagecontent.xsd"' % (
                NAMESPACES['page'],
                NAMESPACES['page'],
                NAMESPACES['page']
            ))
    doc = parsexmlstring_(sio.getvalue())  # pylint: disable=undefined-variable
    # shortcut
    if page and region and line and word and glyph:
        ret += doc.xpath('//page:AlternativeImage/@filename', namespaces=NAMESPACES)
    else:
        if page:
            ret += doc.xpath('/page:PcGts/page:Page/page:AlternativeImage/@filename', namespaces=NAMESPACES)
        if region:
            for class_ in PAGE_REGION_TYPES:
                ret += doc.xpath('//page:%sRegion/page:AlternativeImage/@filename' % class_, namespaces=NAMESPACES)
        if line:
            ret += doc.xpath('//page:TextLine/page:AlternativeImage/@filename', namespaces=NAMESPACES)
        if word:
            ret += doc.xpath('//page:Word/page:AlternativeImage/@filename', namespaces=NAMESPACES)
        if glyph:
            ret += doc.xpath('//page:Glyph/page:AlternativeImage/@filename', namespaces=NAMESPACES)

    return ret
