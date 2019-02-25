"""
API to ``mets:file``
"""
import os

from .ocrd_xml_base import ET
from .constants import NAMESPACES as NS, TAG_METS_FLOCAT, TAG_METS_FILE

class OcrdFile():
    """
    Represents a <mets:file>/<mets:FLocat>
    """

    #  @staticmethod
    #  def create(mimetype, ID, url, local_filename):
    #      el_fileGrp.SubElement('file')

    def __init__(self, el, mimetype=None, instance=None, local_filename=None, mets=None):
        """
        Args:
            el (LxmlElement):
            mimetype (string):
            instance (OcrdFile):
            local_filename (string):
            mets (OcrdMets):
        """
        if el is None:
            el = ET.Element(TAG_METS_FILE)
        self._el = el
        self.mimetype = mimetype
        self.local_filename = local_filename
        self._instance = instance
        self.mets = mets

        #  if baseurl and not local_filename and '://' not in self.url:
        #      self.local_filename = '%s/%s' % (baseurl, self.url)

    def __str__(self):
        """
        String representation
        """
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
        """
        Get the ``os.path.basename`` of the local file, if any.
        """
        return os.path.basename(self.local_filename)

    @property
    def basename_without_extension(self):
        """
        Get the ``os.path.basename`` of the local file, if any, with extension removed.
        """
        ret = self.basename.rsplit('.', 1)[0]
        if ret.endswith('.tar'):
            ret = ret[0:len(ret)-4]
        return ret

    @property
    def ID(self):
        """
        Get the ``ID`` atribute.
        """
        return self._el.get('ID')

    @ID.setter
    def ID(self, ID):
        """
        Set the ``ID`` atribute.
        """
        if ID is None:
            return
        self._el.set('ID', ID)

    @property
    def pageId(self):
        """
        Get the ID of the physical page this file manifests.
        """
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        return self.mets.get_physical_page_for_file(self)

    @pageId.setter
    def pageId(self, pageId):
        """
        Set the ID of the physical page this file manifests.
        """
        if pageId is None:
            return
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        self.mets.set_physical_page_for_file(pageId, self)


    @property
    def mimetype(self):
        """
        Get the ``MIMETYPE``.
        """
        return self._el.get('MIMETYPE')

    @mimetype.setter
    def mimetype(self, mimetype):
        """
        Set the ``MIMETYPE``.
        """
        if mimetype is None:
            return
        self._el.set('MIMETYPE', mimetype)

    @property
    def fileGrp(self):
        """
        The ``USE`` attribute of the containing ``mets:fileGrp``
        """
        return self._el.getparent().get('USE')

    @property
    def url(self):
        """
        Get the ``xlink:href`` of this file.
        """
        el_FLocat = self._el.find(TAG_METS_FLOCAT)
        if el_FLocat is not None:
            return el_FLocat.get("{%s}href" % NS["xlink"])
        return ''

    @url.setter
    def url(self, url):
        """
        Set the ``xlink:href`` of this file.
        """
        if url is None:
            return
        el_FLocat = self._el.find('mets:FLocat', NS)
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        el_FLocat.set("{%s}href" % NS["xlink"], url)
