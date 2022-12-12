"""
API to ``mets:file``
"""
from os.path import splitext, basename

from ocrd_utils import is_local_filename, get_local_filename, MIME_TO_EXT, EXT_TO_MIME

from .ocrd_xml_base import ET
from .constants import NAMESPACES as NS, TAG_METS_FLOCAT, TAG_METS_FILE

class OcrdFile():
    """
    Represents a single ``mets:file/mets:FLocat`` (METS file entry).
    """

    #  @staticmethod
    #  def create(mimetype, ID, url, local_filename):
    #      el_fileGrp.SubElement('file')

    def __init__(self, el, mimetype=None, pageId=None, loctype='OTHER', local_filename=None, mets=None, url=None, ID=None):
        """
        Args:
            el (LxmlElement): etree Element of the ``mets:file`` this represents. Create new if not provided
        Keyword Args:
            mets (OcrdMets): Containing :py:class:`ocrd_models.ocrd_mets.OcrdMets`.
            mimetype (string): ``@MIMETYPE`` of this ``mets:file``
            pageId (string): ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file``
            loctype (string): ``@LOCTYPE`` of this ``mets:file``
            local_filename (string): Local filename
            url (string): ``@xlink:href`` of this ``mets:file``
            ID (string): ``@ID`` of this ``mets:file``
        """
        if el is None:
            raise ValueError("Must provide mets:file element this OcrdFile represents")
        self._el = el
        self.mets = mets
        self.ID = ID
        self.mimetype = mimetype
        self.local_filename = local_filename
        self.loctype = loctype
        self.pageId = pageId

        if url:
            self.url = url

        if not(local_filename):
            if self.url and is_local_filename(self.url):
                self.local_filename = get_local_filename(self.url)

    def __str__(self):
        """
        String representation of this ``mets:file``.
        """
        #  props = '\n\t'.join([
        #      ' : '.join([k, getattr(self, k) if getattr(self, k) else '---'])
        #      for k in ['mimetype', 'ID', 'url', 'local_filename']
        #  ])
        #  return 'OcrdFile[' + '\n\t' + props + '\n\t]'
        props = ', '.join([
            '='.join([k, getattr(self, k) if getattr(self, k) else '---'])
            for k in ['ID', 'mimetype', 'url', 'local_filename']
        ])
        try:
            fileGrp = self.fileGrp
        except ValueError:
            fileGrp = '---'
        return '<OcrdFile fileGrp=%s %s]/> ' % (fileGrp, props)

    def __eq__(self, other):
        return self.ID == other.ID # and \
               # self.url == other.url and \
               # EXT_TO_MIME[MIME_TO_EXT[self.mimetype]] == EXT_TO_MIME[MIME_TO_EXT[other.mimetype]] and \
               # self.fileGrp == other.fileGrp

    @property
    def basename(self):
        """
        Get the ``os.path.basename`` of the local file, if any.
        """
        return basename(self.local_filename if self.local_filename else self.url)

    @property
    def extension(self):
        _basename, ext = splitext(self.basename)
        if _basename.endswith('.tar'):
            ext = ".tar" + ext
        return ext

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
        Get the ``@ID`` of the ``mets:file``.
        """
        return self._el.get('ID')

    @ID.setter
    def ID(self, ID):
        """
        Set the ``@ID`` of the ``mets:file`` to :py:attr:`ID`.
        """
        if ID is None:
            return
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        old_id = self.ID
        self._el.set('ID', ID)
        # also update the references in the physical structmap
        for pageId in self.mets.remove_physical_page_fptr(fileId=old_id):
            self.pageId = pageId

    @property
    def pageId(self):
        """
        Get the ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file`` (physical page manifestation).
        """
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        return self.mets.get_physical_page_for_file(self)

    @pageId.setter
    def pageId(self, pageId):
        """
        Get the ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file`` (physical page manifestation) to :py:attr:`pageId`.
        """
        if pageId is None:
            return
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        self.mets.set_physical_page_for_file(pageId, self)

    @property
    def loctype(self):
        """
        Get the ``@LOCTYPE`` of the ``mets:file``.
        """
        el_FLocat = self._el.find('mets:FLocat', NS)
        return '' if el_FLocat is None else el_FLocat.get('LOCTYPE')

    @loctype.setter
    def loctype(self, loctype):
        """
        Set the ``@LOCTYPE`` of the ``mets:file`` to :py:attr:`loctype`.
        """
        if loctype is None:
            return
        loctype = loctype.upper()
        el_FLocat = self._el.find('mets:FLocat', NS)
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        el_FLocat.set('LOCTYPE', loctype)
        if loctype == 'OTHER':
            self.otherloctype = 'FILE'
        else:
            self.otherloctype = None

    @property
    def otherloctype(self):
        el_FLocat = self._el.find('mets:FLocat', NS)
        return '' if el_FLocat is None else el_FLocat.get('OTHERLOCTYPE')

    @otherloctype.setter
    def otherloctype(self, otherloctype):
        el_FLocat = self._el.find('mets:FLocat', NS)
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        if not otherloctype:
            if 'OTHERLOCTYPE' in el_FLocat.attrib:
                del el_FLocat.attrib['OTHERLOCTYPE']
        else:
            el_FLocat.set('LOCTYPE', 'OTHER')
            el_FLocat.set('OTHERLOCTYPE', otherloctype)

    @property
    def mimetype(self):
        """
        Get the ``@MIMETYPE`` of the ``mets:file``.
        """
        return self._el.get('MIMETYPE')

    @mimetype.setter
    def mimetype(self, mimetype):
        """
        Set the ``@MIMETYPE`` of the ``mets:file`` to :py:attr:`mimetype`.
        """
        if mimetype is None:
            return
        self._el.set('MIMETYPE', mimetype)

    @property
    def fileGrp(self):
        """
        The ``@USE`` of the containing ``mets:fileGrp``
        """
        parent = self._el.getparent()
        if parent is not None:
            return self._el.getparent().get('USE')
        raise ValueError("OcrdFile not related to METS")

    @property
    def url(self):
        """
        Get the ``@xlink:href`` of this ``mets:file``.
        """
        el_FLocat = self._el.find(TAG_METS_FLOCAT)
        if el_FLocat is not None:
            return el_FLocat.get("{%s}href" % NS["xlink"])
        return ''

    @url.setter
    def url(self, url):
        """
        Set the ``@xlink:href`` of this ``mets:file`` to :py:attr:`url`.
        """
        if url is None:
            return
        el_FLocat = self._el.find('mets:FLocat', NS)
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        el_FLocat.set("{%s}href" % NS["xlink"], url)
