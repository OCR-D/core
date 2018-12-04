import os
from ocrd.constants import NAMESPACES as NS, TAG_METS_FLOCAT, TAG_METS_FILE

from .ocrd_xml_base import ET

class OcrdFile(object):
    """
    Represents a <mets:file>/<mets:FLocat>
    """

    #  @staticmethod
    #  def create(mimetype, ID, url, local_filename):
    #      el_fileGrp.SubElement('file')

    def __init__(self, el, mimetype=None, instance=None, local_filename=None, baseurl=''):
        if el is None:
            el = ET.Element(TAG_METS_FILE)
        self._el = el
        self.mimetype = mimetype
        self.local_filename = local_filename
        if baseurl and not local_filename and '://' not in self.url:
            self.local_filename = '%s/%s' % (baseurl, self.url)

        self._instance = instance

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
        ret = self.basename.rsplit('.', 1)[0]
        if ret.endswith('.tar'):
            ret = ret[0:len(ret)-4]
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
    def groupId(self):
        return self._el.get('GROUPID')

    @groupId.setter
    def groupId(self, groupId):
        if groupId is None:
            return
        self._el.set('GROUPID', groupId)

    @property
    def mimetype(self):
        return self._el.get('MIMETYPE')

    @property
    def fileGrp(self):
        """
        The ``USE`` attribute of the parent ``mets:fileGrp``
        """
        return self._el.getparent().get('USE')

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
