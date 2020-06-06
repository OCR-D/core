def get_AllImagePaths(self, page=True, region=True, line=True, alternative_images=True):
    """
    Get all the image paths referenced in the PAGE-XML document.


    page (boolean): Get pc:Page level images
    region (boolean): Get images on pc:*Region level
    line (boolean) Get images on pc:TextLine level
    alternative_images (boolean): Get AlternativeImages as well.
    """
    from .constants import NAMESPACES
    ret = []
    if page:
        return self.get_PageType().get('imageFilename')
    if alternative_images:
        # XXX Since we're only interested in the **paths** of the images,
        # export, parse and xpath are less convoluted than traversing
        # the generateDS API. Quite possibly not as efficient as could be.
        from io import StringIO
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
        # XXX _parsexml parses file with lxml
        doc = parsexml_(sio.getvalue())
        if page:
            for ai in doc.xpath('/page:PcGts/page:Page/page:AlternativeImage', namespaces=NAMESPACES):
                print(ai)



