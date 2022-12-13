"""
Validating a workspace.
"""
import re
from traceback import format_exc
from pathlib import Path

from ocrd_utils import getLogger, MIMETYPE_PAGE, pushd_popd, is_local_filename
from ocrd_models import ValidationReport
from ocrd_modelfactory import page_from_file

from .constants import FILE_GROUP_CATEGORIES, FILE_GROUP_PREFIX
from .page_validator import PageValidator
from .xsd_page_validator import XsdPageValidator
from .xsd_mets_validator import XsdMetsValidator

#
# -------------------------------------------------
#

class WorkspaceValidator():
    """
    Validates an OCR-D/METS workspace against the specs.
    """

    @staticmethod
    def check_file_grp(workspace, input_file_grp=None, output_file_grp=None, page_id=None, report=None):
        """
        Return a report on whether input_file_grp is/are in workspace.mets and output_file_grp is/are not.
        To be run before processing

        Arguments:
            workspacec (Workspace) the workspace to validate
            input_file_grp (list|string)  list or comma-separated list of input file groups
            output_file_grp (list|string) list or comma-separated list of output file groups
            page_id (list|string) list or comma-separated list of page_ids to write to
        """
        if not report:
            report = ValidationReport()
        if isinstance(input_file_grp, str):
            input_file_grp = input_file_grp.split(',') if input_file_grp else []
        if isinstance(output_file_grp, str):
            output_file_grp = output_file_grp.split(',') if output_file_grp else []
        if page_id and isinstance(page_id, str):
            page_id = page_id.split(',')

        log = getLogger('ocrd.workspace_validator')
        log.debug("input_file_grp=%s output_file_grp=%s" % (input_file_grp, output_file_grp))
        if input_file_grp:
            for grp in input_file_grp:
                if grp not in workspace.mets.file_groups:
                    report.add_error("Input fileGrp[@USE='%s'] not in METS!" % grp)
        if output_file_grp:
            for grp in output_file_grp:
                if grp in workspace.mets.file_groups:
                    if page_id:
                        for one_page_id in page_id:
                            if next(workspace.mets.find_files(fileGrp=grp, pageId=one_page_id), None):
                                report.add_error("Output fileGrp[@USE='%s'] already contains output for page %s" % (grp, one_page_id))
                    else:
                        report.add_error("Output fileGrp[@USE='%s'] already in METS!" % grp)
        return report

    def __init__(self, resolver, mets_url, src_dir=None, skip=None, download=False,
                 page_strictness='strict', page_coordinate_consistency='poly'):
        """
        Construct a new WorkspaceValidator.

        Args:
            resolver (Resolver):
            mets_url (string):
            src_dir (string):
            skip (list):
            download (boolean):
            page_strictness ("strict"|"lax"|"fix"|"off"):
            page_coordinate_consistency ("poly"|"baseline"|"both"|"off"):
        """
        self.report = ValidationReport()
        self.skip = skip if skip else []
        self.log = getLogger('ocrd.workspace_validator')
        self.log.debug('resolver=%s mets_url=%s src_dir=%s', resolver, mets_url, src_dir)
        self.resolver = resolver
        if mets_url is None and src_dir is not None:
            mets_url = '%s/mets.xml' % src_dir
        self.mets_url = mets_url
        self.download = download
        self.page_strictness = page_strictness
        self.page_coordinate_consistency = page_coordinate_consistency

        self.src_dir = src_dir
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
            skip (list): Tests to skip. One or more of 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'dimension', 'url'
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
        except Exception as e: # pylint: disable=broad-except
            self.log.warning("Failed to instantiate workspace: %s", e)
            self.report.add_error("Failed to instantiate workspace: %s" % e)
            return self.report
        with pushd_popd(self.workspace.directory):
            try:
                if 'mets_unique_identifier' not in self.skip:
                    self._validate_mets_unique_identifier()
                if 'mets_file_group_names' not in self.skip:
                    self._validate_mets_file_group_names()
                if 'mets_files' not in self.skip:
                    self._validate_mets_files()
                if 'pixel_density' not in self.skip:
                    self._validate_pixel_density()
                if 'multipage' not in self.skip:
                    self._validate_multipage()
                if 'dimension' not in self.skip:
                    self._validate_dimension()
                if 'imagefilename' not in self.skip:
                    self._validate_imagefilename()
                if 'page' not in self.skip:
                    self._validate_page()
                if 'page_xsd' not in self.skip:
                    self._validate_page_xsd()
                if 'mets_xsd' not in self.skip:
                    self._validate_mets_xsd()
            except Exception: # pylint: disable=broad-except
                self.report.add_error("Validation aborted with exception: %s" % format_exc())
        return self.report

    def _resolve_workspace(self):
        """
        Clone workspace from mets_url unless workspace was provided.
        """
        self.log.debug('_resolve_workspace')
        if self.workspace is None:
            self.workspace = self.resolver.workspace_from_url(self.mets_url, src_baseurl=self.src_dir, download=self.download)
            self.mets = self.workspace.mets

    def _validate_mets_unique_identifier(self):
        """
        Validate METS unique identifier exists.

        See `spec <https://ocr-d.github.io/mets#unique-id-for-the-document-processed>`_.
        """
        self.log.debug('_validate_mets_unique_identifier')
        if self.mets.unique_identifier is None:
            self.report.add_error("METS has no unique identifier")

    def _validate_imagefilename(self):
        """
        Validate that the imageFilename is correctly set to a filename relative to the workspace
        """
        self.log.debug('_validate_imagefilename')
        for f in self.mets.find_files(mimetype=MIMETYPE_PAGE):
            if not is_local_filename(f.url) and not self.download:
                self.report.add_notice("Won't download remote PAGE XML <%s>" % f.url)
                continue
            self.workspace.download_file(f)
            page = page_from_file(f).get_Page()
            imageFilename = page.imageFilename
            if not self.mets.find_files(url=imageFilename):
                self.report.add_error("PAGE-XML %s : imageFilename '%s' not found in METS" % (f.url, imageFilename))
            if is_local_filename(imageFilename) and not Path(imageFilename).exists():
                self.report.add_warning("PAGE-XML %s : imageFilename '%s' points to non-existent local file" % (f.url, imageFilename))

    def _validate_dimension(self):
        """
        Validate image height and PAGE imageHeight match
        """
        self.log.info('_validate_dimension')
        for f in self.mets.find_files(mimetype=MIMETYPE_PAGE):
            if not is_local_filename(f.url) and not self.download:
                self.report.add_notice("_validate_dimension: Not executed because --download wasn't set and PAGE might reference remote (Alternative)Images <%s>" % f.url)
                continue
            page = page_from_file(f).get_Page()
            _, _, exif = self.workspace.image_from_page(page, f.pageId)
            if page.imageHeight != exif.height:
                self.report.add_error("PAGE '%s': @imageHeight != image's actual height (%s != %s)" % (f.ID, page.imageHeight, exif.height))
            if page.imageWidth != exif.width:
                self.report.add_error("PAGE '%s': @imageWidth != image's actual width (%s != %s)" % (f.ID, page.imageWidth, exif.width))

    def _validate_multipage(self):
        """
        Validate the number of images per file is 1 (TIFF allows multi-page images)

        See `spec <https://ocr-d.github.io/mets#no-multi-page-images>`_.
        """
        self.log.debug('_validate_multipage')
        for f in [f for f in self.mets.find_files() if f.mimetype.startswith('image/')]:
            if not is_local_filename(f.url) and not self.download:
                self.report.add_notice("Won't download remote image <%s>" % f.url)
                continue
            try:
                exif = self.workspace.resolve_image_exif(f.url)
                if exif.n_frames > 1:
                    self.report.add_error("Image %s: More than 1 frame: %s" % (f.ID, exif.n_frames))
            except FileNotFoundError:
                self.report.add_error("Image %s: Could not retrieve %s" % (f.ID, f.url))
                return

    def _validate_pixel_density(self):
        """
        Validate image pixel density

        See `spec <https://ocr-d.github.io/mets#pixel-density-of-images-must-be-explicit-and-high-enough>`_.
        """
        self.log.debug('_validate_pixel_density')
        for f in [f for f in self.mets.find_files() if f.mimetype.startswith('image/')]:
            if not is_local_filename(f.url) and not self.download:
                self.report.add_notice("Won't download remote image <%s>" % f.url)
                continue
            exif = self.workspace.resolve_image_exif(f.url)
            for k in ['xResolution', 'yResolution']:
                v = exif.__dict__.get(k)
                if v is None or v <= 72:
                    self.report.add_notice("Image %s: %s (%s pixels per %s) is suspiciously low" % (f.ID, k, v, exif.resolutionUnit))

    def _validate_mets_file_group_names(self):
        """
        Ensure ``USE`` attributes of ``mets:fileGrp`` conform to OCR-D naming schema..

        See `spec <https://ocr-d.github.io/mets#file-group-use-syntax>`_.
        """
        self.log.debug('_validate_mets_file_group_names')
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
                    self.report.add_notice("Unspecified USE category '%s' in fileGrp '%s'" % (category, fileGrp))
                if name is not None and not re.match(r'^[A-Z0-9-]{3,}$', name):
                    self.report.add_notice("Invalid USE name '%s' in fileGrp '%s'" % (name, fileGrp))

    def _validate_mets_files(self):
        """
        Validate ``mets:file`` URLs are sane.
        """
        self.log.debug('_validate_mets_files')
        try:
            next(self.mets.find_files())
        except StopIteration:
            self.report.add_error("No files")
        for f in self.mets.find_files():
            if f._el.get('GROUPID'): # pylint: disable=protected-access
                self.report.add_notice("File '%s' has GROUPID attribute - document might need an update" % f.ID)
            if not f.pageId:
                self.report.add_error("File '%s' does not manifest any physical page." % f.ID)
            if not f.url:
                self.report.add_error("File '%s' has no mets:Flocat/@xlink:href" % f.ID)
                continue
            if 'url' not in self.skip and ':/' in f.url:
                if re.match(r'^file:/[^/]', f.url):
                    self.report.add_error("File '%s' has an invalid (Java-specific) file URL '%s'" % (f.ID, f.url))
                scheme = f.url[0:f.url.index(':')]
                if scheme not in ('http', 'https', 'file'):
                    self.report.add_warning("File '%s' has non-HTTP, non-file URL '%s'" % (f.ID, f.url))

    def _validate_page(self):
        """
        Run PageValidator on the PAGE-XML documents referenced in the METS.
        """
        self.log.debug('_validate_page')
        for ocrd_file in self.mets.find_files(mimetype=MIMETYPE_PAGE):
            self.workspace.download_file(ocrd_file)
            page_report = PageValidator.validate(ocrd_file=ocrd_file,
                                                 page_textequiv_consistency=self.page_strictness,
                                                 check_coords=self.page_coordinate_consistency in ['poly', 'both'],
                                                 check_baseline=self.page_coordinate_consistency in ['baseline', 'both'])
            pg = page_from_file(ocrd_file)
            if pg.pcGtsId != ocrd_file.ID:
                page_report.add_warning('pc:PcGts/@pcGtsId differs from mets:file/@ID: "%s" !== "%s"' % (pg.pcGtsId or '', ocrd_file.ID or ''))
            self.report.merge_report(page_report)

    def _validate_page_xsd(self):
        """
        Validate all PAGE-XML files against PAGE XSD schema
        """
        self.log.debug('_validate_page_xsd')
        for ocrd_file in self.mets.find_files(mimetype=MIMETYPE_PAGE):
            self.workspace.download_file(ocrd_file)
            for err in XsdPageValidator.validate(Path(ocrd_file.local_filename)).errors:
                self.report.add_error("%s: %s" % (ocrd_file.ID, err))
        self.log.debug("Finished alidating all PAGE-XML files against XSD")

    def _validate_mets_xsd(self):
        """
        Validate METS against METS XSD schema
        """
        self.log.debug('_validate_mets_xsd')
        self.log.debug("Validating METS %s against XSD" % self.workspace.mets_target)
        for err in XsdMetsValidator.validate(Path(self.workspace.mets_target)).errors:
            self.report.add_error("%s: %s" % (self.workspace.mets_target, err))
        self.log.debug("Finished Validating METS against XSD")
