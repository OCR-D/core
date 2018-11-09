from tempfile import mkdtemp
from shutil import rmtree

from bagit import Bag
from bagit_profile import Profile, ProfileValidationError # pylint: disable=no-name-in-module

from ..constants import OCRD_BAGIT_PROFILE_URL, OCRD_BAGIT_PROFILE, TMP_BAGIT_PREFIX
from ..utils import getLogger, unzip_file_to_dir
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

    def __init__(self, resolver, path_to_zip):
        """
        Arguments:
            resolver (Resolver): resolver
            path_to_zip (string): Path to the OCRD-ZIP file
        """
        self.resolver = resolver
        self.path_to_zip = path_to_zip
        self.report = ValidationReport()
        self.profile_validator = Profile(OCRD_BAGIT_PROFILE_URL, profile=OCRD_BAGIT_PROFILE)

    def validate(self):
        try:
            self.profile_validator.validate_serialization(self.path_to_zip)
        except (IOError, ProfileValidationError) as err:
            self.report.add_error(err.value)
        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)
        unzip_file_to_dir(self.path_to_zip, bagdir)
        bag = Bag(bagdir)
        self.profile_validator.validate(bag)
        rmtree(bagdir)
        return self.report
