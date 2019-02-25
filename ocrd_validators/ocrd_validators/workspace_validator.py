"""
Validating a workspace.
"""
import re

from ocrd_utils import getLogger, MIMETYPE_PAGE
from .constants import FILE_GROUP_CATEGORIES, FILE_GROUP_PREFIX
from .report import ValidationReport
from .page_validator import PageValidator

log = getLogger('ocrd.workspace_validator')

#
# -------------------------------------------------
#

class WorkspaceValidator():
    """
    Validates an OCR-D/METS workspace against the specs.
    """

    def __init__(self, resolver, mets_url, src_dir=None, skip=None, download=False, page_strictness='strict'):
        """
        Construct a new WorkspaceValidator.

        Args:
            resolver (Resolver):
            mets_url (string):
            src_dir (string):
            skip (list):
            download (boolean):
            page_strictness ("strict"|"lax"|"fix"|"off"):
        """
        self.report = ValidationReport()
        self.skip = skip if skip else []
        log.debug('resolver=%s mets_url=%s src_dir=%s', resolver, mets_url, src_dir)
        self.resolver = resolver
        self.mets_url = mets_url
        self.download = download
        self.page_strictness = page_strictness

        self.src_dir = src_dir
        if mets_url is None and src_dir is not None:
            mets_url = '%s/mets.xml' % src_dir
        self.workspace = None
        self.mets = None

    @staticmethod
    def validate(*args, **kwargs):
        """
        Validates the workspace of a METS URL against the specs

        Arguments:
            resolver (:class:`ocrd.Resolver`): Resolver
            mets_url (string): URL of the METS file
            src_dir (string, None): Directory containing mets file
            skip (list): Tests to skip. One or more of 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'url'
            download (boolean): Whether to download files

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        validator = WorkspaceValidator(*args, **kwargs)
        return validator._validate() # pylint: disable=protected-access

    def _validate(self):
        """
        Actual validation.
        """
        try:
            self._resolve_workspace()
            if 'mets_unique_identifier' not in self.skip:
                self._validate_mets_unique_identifier()
            if 'mets_file_group_names' not in self.skip:
                self._validate_mets_file_group_names()
            if 'mets_files' not in self.skip:
                self._validate_mets_files()
            if 'pixel_density' not in self.skip:
                self._validate_pixel_density()
            if 'page' not in self.skip:
                self._validate_page()
        except Exception as e: # pylint: disable=broad-except
            self.report.add_error("Failed to instantiate workspace: %s" % e)
            #  raise e
        return self.report

    def _resolve_workspace(self):
        """
        Clone workspace from mets_url unless workspace was provided.
        """
        if self.workspace is None:
            self.workspace = self.resolver.workspace_from_url(self.mets_url, baseurl=self.src_dir, download=self.download)
            self.mets = self.workspace.mets

    def _validate_mets_unique_identifier(self):
        """
        Validate METS unique identifier exists.

        See `spec <https://ocr-d.github.io/mets#unique-id-for-the-document-processed>`_.
        """
        if self.mets.unique_identifier is None:
            self.report.add_error("METS has no unique identifier")

    def _validate_pixel_density(self):
        """
        Validate image pixel density

        See `spec <https://ocr-d.github.io/mets#pixel-density-of-images-must-be-explicit-and-high-enough>`_.
        """
        for f in [f for f in self.mets.find_files() if f.mimetype.startswith('image/')]:
            if not f.local_filename and not self.download:
                self.report.add_notice("Won't download remote image <%s>" % f.url)
                continue
            exif = self.workspace.resolve_image_exif(f.url)
            for k in ['xResolution', 'yResolution']:
                v = exif.__dict__.get(k)
                if v is None or v <= 72:
                    self.report.add_error("Image %s: %s (%s pixels per %s) is too low" % (f.ID, k, v, exif.resolutionUnit))

    def _validate_mets_file_group_names(self):
        """
        Ensure ``USE`` attributes of ``mets:fileGrp`` conform to OCR-D naming schema..

        See `spec <https://ocr-d.github.io/mets#file-group-use-syntax>`_.
        """
        for fileGrp in self.mets.file_groups:
            if not fileGrp.startswith(FILE_GROUP_PREFIX):
                self.report.add_notice("fileGrp USE does not begin with '%s': %s" % (FILE_GROUP_PREFIX, fileGrp))
            else:
                # OCR-D-FOO-BAR -> ('FOO', 'BAR')
                # \____/\_/ \_/
                #   |    |   |
                # Prefix |  Name
                #     Category
                category = fileGrp[len(FILE_GROUP_PREFIX):]
                name = None
                if '-' in category:
                    category, name = category.split('-', 1)
                if category not in FILE_GROUP_CATEGORIES:
                    self.report.add_error("Unspecified USE category '%s' in fileGrp '%s'" % (category, fileGrp))
                if name is not None and not re.match(r'^[A-Z0-9-]{3,}$', name):
                    self.report.add_error("Invalid USE name '%s' in fileGrp '%s'" % (name, fileGrp))

    def _validate_mets_files(self):
        """
        Validate ``mets:file`` URLs are sane.
        """
        if not self.mets.find_files():
            self.report.add_error("No files")
        for f in self.mets.find_files():
            if f._el.get('GROUPID'): # pylint: disable=protected-access
                self.report.add_notice("File '%s' has GROUPID attribute - document might need an update" % f.ID)
            if not f.pageId:
                self.report.add_error("File '%s' does not manifest any physical page." % f.ID)
            if 'url' not in self.skip and ':/' in f.url:
                if re.match(r'^file:/[^/]', f.url):
                    self.report.add_warning("File '%s' has an invalid (Java-specific) file URL '%s'" % (f.ID, f.url))
                scheme = f.url[0:f.url.index(':')]
                if scheme not in ('http', 'https', 'file'):
                    self.report.add_warning("File '%s' has non-HTTP, non-file URL '%s'" % (f.ID, f.url))

    def _validate_page(self):
        """
        Run PageValidator on the PAGE-XML documents referenced in the METS.
        """
        for ocrd_file in self.mets.find_files(mimetype=MIMETYPE_PAGE, local_only=True):
            self.workspace.download_file(ocrd_file)
            page_report = PageValidator.validate(ocrd_file=ocrd_file, strictness=self.page_strictness)
            self.report.merge_report(page_report)
