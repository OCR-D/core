from bagit_profile import Profile, ProfileValidationError

from ..constants import OCRD_BAGIT_PROFILE_URL
from ..utils import getLogger
from .report import ValidationReport

log = getLogger('ocrd.ocrd_zip_validator')

#
# -------------------------------------------------
#

class OcrdZipValidator(object):
    """
    Validate conformance with BagIt and OCR-D bagit profile.

    See:
        - https://ocr-d.github.io/ocrd_zip
        - https://ocr-d.github.io/bagit-profile.json
        - https://ocr-d.github.io/bagit-profile.yml
    """

    def __init__(self, resolver, bagzip):
        """
        Arguments:
            resolver (Resolver): resolver
            bagzip (string): Path to the OCRD-ZIP file
        """
        self.resolver = resolver
        self.bagzip = bagzip
        self.report = ValidationReport()
        self.profile_validator = Profile(OCRD_BAGIT_PROFILE_URL)

    def validate(self):
        try:
            self.profile_validator.validate_serialization(self.bagzip)
        except (IOError, ProfileValidationError) as err:
            self.report.add_error(err.value)
        #  self._validate_serialization()
        #  self._ensure_bagdir
        #  self._validate_mets_file_group_names()
        #  self._validate_mets_files()
        #  self._validate_pixel_density()
        return self.report
