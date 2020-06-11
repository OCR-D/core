"""
API to ``mets:file``
"""
from os.path import splitext, basename

from ocrd_utils import is_local_filename, get_local_filename

from .ocrd_xml_base import ET
from .constants import NAMESPACES as NS, TAG_METS_FLOCAT, TAG_METS_FILE

class OcrdFile():
    """
    Represents a <mets:file>/<mets:FLocat>
    """

    #  @staticmethod
    #  def create(mimetype, ID, url, local_filename):
    #      el_fileGrp.SubElement('file')

    def __init__(self, el, mimetype=None, pageId=None, loctype='OTHER', local_filename=None, mets=None, url=None, ID=None):
        """
        Args:
            el (LxmlElement): etree Element of the mets:file this represents. Create new if not provided
            mimetype (string): MIME type of the file
            pageId (string): ID of the physical page
            loctype (string): METS @LOCTYPE
            local_filename (string): Local filename
            mets (OcrdMets): Containing OcrdMets
            url (string): xlink:href of the file
            ID (string): @ID of the mets:file
        """
        if el is None:
            el = ET.Element(TAG_METS_FILE)
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
        Get the ``ID`` attribute.
        """
        return self._el.get('ID')

    @ID.setter
    def ID(self, ID):
        """
        Set the ``ID`` attribute.
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
    def loctype(self):
        """
        Get the ``LOCTYPE``.
        """
        el_FLocat = self._el.find('mets:FLocat', NS)
        return '' if el_FLocat is None else el_FLocat.get('LOCTYPE')

    @loctype.setter
    def loctype(self, loctype):
        """
        Set the ``LOCTYPE``.
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
        parent = self._el.getparent()
        if parent is not None:
            return self._el.getparent().get('USE')
        return 'TEMP'

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
