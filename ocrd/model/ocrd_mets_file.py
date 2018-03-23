from ocrd.constants import NAMESPACES as NS

class OcrdMetsFile(object):
    """
    Represents a <mets:file>/<mets:FLocat>
    """

    def __init__(self, el, filename=None):
        self.mimetype = el.get('MIMETYPE')
        self.ID = el.get('ID')
        self.url = el.find('mets:FLocat', NS).get("{%s}href" % NS["xlink"])
        self.filename = filename

    def __str__(self):
        return 'OcrdMetsFile[%s @ %s locally: "%s"]' % (self.mimetype, self.url, self.filename)
