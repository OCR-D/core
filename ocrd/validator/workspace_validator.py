import re

from ocrd.constants import FILE_GROUP_CATEGORIES, FILE_GROUP_PREFIX
from .report import ValidationReport
from ocrd.utils import getLogger

log = getLogger('ocrd.workspace_validator')

#
# -------------------------------------------------
#

class WorkspaceValidator(object):
    """
    Validates an OCR-D/METS workspace against the specs.

    Args:
        resolver (:class:`Resolver`) : Instance of a resolver
        mets_url (string) : URL of the METS file
    """

    def __init__(self, resolver, mets_url, directory=None):
        self.resolver = resolver
        self.mets_url = mets_url
        self.report = ValidationReport()
        log.debug('resolver=%s mets_url=%s directory=%s', resolver, mets_url, directory)
        if mets_url is None:
            mets_url = '%s/mets.xml' % directory
        self.workspace = self.resolver.workspace_from_url(mets_url, directory=directory)
        self.mets = self.workspace.mets

    @staticmethod
    def validate_url(resolver, mets_url, directory=None):
        """
        Validates the workspace of a METS URL against the specs

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        validator = WorkspaceValidator(resolver, mets_url, directory=directory)
        return validator.validate()

    def validate(self):
        self._validate_mets_unique_identifier()
        self._validate_mets_file_group_names()
        self._validate_mets_files()
        self._validate_pixel_density()
        return self.report

    def _validate_mets_unique_identifier(self):
        if self.mets.unique_identifier is None:
            self.report.add_error("METS has no unique identifier")

    def _validate_pixel_density(self):
        for f in [f for f in self.mets.find_files() if f.mimetype.startswith('image/')]:
            exif = self.workspace.resolve_image_exif(f.url)
            for k in ['xResolution', 'yResolution']:
                v = exif.__dict__.get(k)
                if v is None or v <= 72:
                    self.report.add_error("Image %s: %s (%s pixels per %s) is too low" % (f.ID, k, v, exif.resolutionUnit))

    def _validate_mets_file_group_names(self):
        for fileGrp in self.mets.file_groups:
            if not fileGrp.startswith(FILE_GROUP_PREFIX):
                self.report.add_warning("fileGrp USE does not begin with '%s': %s" % (FILE_GROUP_PREFIX, fileGrp))
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
        if not self.mets.find_files():
            self.report.add_error("No files")
