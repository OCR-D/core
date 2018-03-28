import os
from ocrd.constants import NAMESPACES as NS, TAG_METS_FLOCAT
from ocrd.utils import getLogger, filename_without_extension

from .ocrd_xml_base import ET

log = getLogger('OcrdFile')

class OcrdFile(object):
    """
    Represents a <mets:file>/<mets:FLocat>
    """

    #  @staticmethod
    #  def create(mimetype, ID, url, local_filename):
    #      el_fileGrp.SubElement('file')

    def __init__(self, el, instance=None, local_filename=None, workspace=None):
        self._el = el
        self.local_filename = local_filename
        self._instance = instance
        self.workspace = workspace

    def __str__(self):
        #  props = '\n\t'.join([
        #      ' : '.join([k, getattr(self, k) if getattr(self, k) else '---'])
        #      for k in ['mimetype', 'ID', 'url', 'local_filename']
        #  ])
        #  return 'OcrdFile[' + '\n\t' + props + '\n\t]'
        props = ', '.join([
            '='.join([k, getattr(self, k) if getattr(self, k) else '---'])
            for k in ['mimetype', 'ID', 'url', 'local_filename']
        ])
        return '<OcrdFile ' + props + ']/> '

    @property
    def basename(self):
        return os.path.basename(self.local_filename)

    @property
    def basename_without_extension(self):
        (ret, _) = filename_without_extension(self.basename)
        return ret

    @property
    def ID(self):
        return self._el.get('ID')

    @ID.setter
    def ID(self, ID):
        if ID is None:
            return
        self._el.set('ID', ID)

    @property
    def mimetype(self):
        return self._el.get('MIMETYPE')

    @mimetype.setter
    def mimetype(self, mimetype):
        if mimetype is None:
            return
        self._el.set('MIMETYPE', mimetype)

    @property
    def url(self):
        el_FLocat = self._el.find(TAG_METS_FLOCAT)
        if el_FLocat is not None:
            return el_FLocat.get("{%s}href" % NS["xlink"])

    @url.setter
    def url(self, url):
        if url is None:
            return
        el_FLocat = self._el.find('mets:FLocat', NS)
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        el_FLocat.set("{%s}href" % NS["xlink"], url)
