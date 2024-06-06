"""
API to ``mets:file``
"""
from pathlib import Path
from typing import Any, List, Optional, Union

from ocrd_utils import deprecation_warning

from .ocrd_xml_base import ET # type: ignore
from .constants import NAMESPACES as NS, TAG_METS_FLOCAT

class OcrdFile():
    """
    Represents a single ``mets:file/mets:FLocat`` (METS file entry).
    """

    def __init__(self, el, mimetype=None, pageId=None, local_filename=None, mets=None, url=None, ID=None, loctype=None):
        """
        Args:
            el (LxmlElement): etree Element of the ``mets:file`` this represents. Create new if not provided
        Keyword Args:
            mets (OcrdMets): Containing :py:class:`ocrd_models.ocrd_mets.OcrdMets`.
            mimetype (string): ``@MIMETYPE`` of this ``mets:file``
            pageId (string): ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file``
            url (string): original ``@xlink:href`` of this ``mets:file``
            local_filename (string): ``@xlink:href`` pointing to the locally cached version of the file in the workspace
            ID (string): ``@ID`` of this ``mets:file``
            loctype (string): DEPRECATED do not use
        """
        if el is None:
            raise ValueError("Must provide mets:file element this OcrdFile represents")
        if loctype:
            deprecation_warning("'loctype' is not supported in OcrdFile anymore, use 'url' or 'local_filename'")
        self._el = el
        self.mets = mets
        self.ID = ID
        self.mimetype = mimetype
        self.pageId = pageId

        if local_filename:
            self.local_filename = local_filename
        if url:
            self.url = url

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
            '='.join([k, str(getattr(self, k)) if getattr(self, k) else '---'])
            for k in ['ID', 'mimetype', 'url', 'local_filename']
        ])
        try:
            fileGrp = self.fileGrp
        except ValueError:
            fileGrp = '---'
        return '<OcrdFile fileGrp=%s %s]/> ' % (fileGrp, props)

    def __eq__(self, other):
        return self.ID == other.ID \
           and self.url == other.url \
           and self.local_filename == other.local_filename
               # EXT_TO_MIME[MIME_TO_EXT[self.mimetype]] == EXT_TO_MIME[MIME_TO_EXT[other.mimetype]] and \
               # self.fileGrp == other.fileGrp

    @property
    def basename(self) -> str:
        """
        Get the ``.name`` of the local file
        """
        if not self.local_filename:
            return ''
        return Path(self.local_filename).name

    @property
    def extension(self) -> str:
        if not self.local_filename:
            return ''
        return ''.join(Path(self.local_filename).suffixes)

    @property
    def basename_without_extension(self) -> str:
        """
        Get the ``os.path.basename`` of the local file, if any, with extension removed.
        """
        if not self.local_filename:
            return ''
        return Path(self.local_filename).name[:-len(self.extension)]

    @property
    def ID(self) -> str:
        """
        Get the ``@ID`` of the ``mets:file``.
        """
        return self._el.get('ID')

    @ID.setter
    def ID(self, ID : Optional[str]) -> None:
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
    def pageId(self) -> str:
        """
        Get the ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file`` (physical page manifestation).
        """
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        return self.mets.get_physical_page_for_file(self)

    @pageId.setter
    def pageId(self, pageId : Optional[str]) -> None:
        """
        Get the ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file`` (physical page manifestation) to :py:attr:`pageId`.
        """
        if pageId is None:
            return
        if self.mets is None:
            raise Exception("OcrdFile %s has no member 'mets' pointing to parent OcrdMets" % self)
        self.mets.set_physical_page_for_file(pageId, self)

    @property
    def loctypes(self) -> List[str]:
        """
        Get the ``@LOCTYPE``s of the ``mets:file``.
        """
        return [x.get('LOCTYPE') for x in  self._el.findall('mets:FLocat', NS)]

    @property
    def mimetype(self) -> str:
        """
        Get the ``@MIMETYPE`` of the ``mets:file``.
        """
        return self._el.get('MIMETYPE')

    @mimetype.setter
    def mimetype(self, mimetype : Optional[str]) -> None:
        """
        Set the ``@MIMETYPE`` of the ``mets:file`` to :py:attr:`mimetype`.
        """
        if mimetype is None:
            return
        self._el.set('MIMETYPE', mimetype)

    @property
    def fileGrp(self) -> str:
        """
        The ``@USE`` of the containing ``mets:fileGrp``
        """
        parent = self._el.getparent()
        if parent is not None:
            return self._el.getparent().get('USE')
        raise ValueError("OcrdFile not related to METS")

    @property
    def url(self) -> str:
        """
        Get the remote/original URL ``@xlink:href`` of this ``mets:file``.
        """
        el_FLocat = self._el.find('mets:FLocat[@LOCTYPE="URL"]', NS)
        if el_FLocat is not None:
            return el_FLocat.get("{%s}href" % NS["xlink"])
        return ''

    @url.setter
    def url(self, url : Optional[str]) -> None:
        """
        Set the remote/original URL ``@xlink:href`` of this ``mets:file`` to :py:attr:`url`.
        """
        el_FLocat = self._el.find('mets:FLocat[@LOCTYPE="URL"]', NS)
        if url is None:
            if el_FLocat is not None:
                self._el.remove(el_FLocat)
            return
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        el_FLocat.set("{%s}href" % NS["xlink"], url)
        el_FLocat.set("LOCTYPE", "URL")

    @property
    def local_filename(self) -> Optional[str]:
        """
        Get the local/cached ``@xlink:href`` of this ``mets:file``.
        """
        el_FLocat = self._el.find('mets:FLocat[@LOCTYPE="OTHER"][@OTHERLOCTYPE="FILE"]', NS)
        if el_FLocat is not None:
            return el_FLocat.get("{%s}href" % NS["xlink"])
        return None

    @local_filename.setter
    def local_filename(self, fname : Optional[Union[Path, str]]):
        """
        Set the local/cached ``@xlink:href`` of this ``mets:file`` to :py:attr:`local_filename`.
        """
        el_FLocat = self._el.find('mets:FLocat[@LOCTYPE="OTHER"][@OTHERLOCTYPE="FILE"]', NS)
        if not fname:
            if el_FLocat is not None:
                self._el.remove(el_FLocat)
            return
        else:
            fname = str(fname)
        if el_FLocat is None:
            el_FLocat = ET.SubElement(self._el, TAG_METS_FLOCAT)
        el_FLocat.set("{%s}href" % NS["xlink"], fname)
        el_FLocat.set("LOCTYPE", "OTHER")
        el_FLocat.set("OTHERLOCTYPE", "FILE")


class ClientSideOcrdFile:
    """
    Provides the same interface as :py:class:`ocrd_models.ocrd_file.OcrdFile`
    but without attachment to :py:class:`ocrd_models.ocrd_mets.OcrdMets` since
    this represents the response of the :py:class:`ocrd.mets_server.OcrdMetsServer`.
    """

    def __init__(
        self,
        el,
        mimetype: str = '',
        pageId: str = '',
        loctype: str ='OTHER',
        local_filename: Optional[str] = None,
        mets : Any = None,
        url: str = '',
        ID: str = '',
        fileGrp: str = ''
    ):
        """
        Args:
            el (): ignored
        Keyword Args:
            mets (): ignored
            mimetype (string): ``@MIMETYPE`` of this ``mets:file``
            pageId (string): ``@ID`` of the physical ``mets:structMap`` entry corresponding to this ``mets:file``
            loctype (string): ``@LOCTYPE`` of this ``mets:file``
            url (string): ignored XXX the remote/original file once we have proper mets:FLocat bookkeeping 
            local_filename (): ``@xlink:href`` of this ``mets:file`` - XXX the local file once we have proper mets:FLocat bookkeeping
            ID (string): ``@ID`` of this ``mets:file``
        """
        self.ID = ID
        self.mimetype = mimetype
        self.local_filename = local_filename
        self.url = url
        self.loctype = loctype
        self.pageId = pageId
        self.fileGrp = fileGrp

    def __str__(self):
        props = ', '.join([
            '='.join([k, getattr(self, k) if hasattr(self, k) and getattr(self, k) else '---'])
            for k in ['fileGrp', 'ID', 'mimetype', 'url', 'local_filename']
        ])
        return '<ClientSideOcrdFile %s]/>' % (props)
