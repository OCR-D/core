"""
Validating OCRD-ZIP.

See `spec <https://ocr-d.github.io/ocrd_zip>`_.
"""
from tempfile import mkdtemp
from shutil import rmtree

from ocrd_utils import getLogger, unzip_file_to_dir

from bagit import Bag, BagValidationError # pylint: disable=no-name-in-module
from bagit_profile import Profile, ProfileValidationError # pylint: disable=no-name-in-module

from .constants import OCRD_BAGIT_PROFILE, OCRD_BAGIT_PROFILE_URL, TMP_BAGIT_PREFIX
from .report import ValidationReport

log = getLogger('ocrd.ocrd_zip_validator')

#
# -------------------------------------------------
#

class OcrdZipValidator():
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

    def _validate_profile(self, bag):
        """
        Validate against OCRD BagIt profile (bag-info fields, algos etc)
        """
        if not self.profile_validator.validate(bag):
            raise Exception(str(self.profile_validator.report))

    def _validate_bag(self, bag, **kwargs):
        """
        Validate BagIt (checksums, payload.oxum etc)
        """
        failed = None
        try:
            bag.validate(**kwargs)
        except BagValidationError as e:
            failed = e
            #  for d in e.details:
            #      if isinstance(d, ChecksumMismatch):
            #          log.error("Validation Error: expected %s to have %s checksum of %s but found %s", d.path, d.algorithm, d.expected, d.found)
            #      else:
            #          log.error("Validation Error: %s", d)
        if failed:
            raise BagValidationError("%s" % failed)

    def validate(self, skip_checksums=False, skip_bag=False, skip_unzip=False, skip_delete=False, processes=2):
        """
        Validate an OCRD-ZIP file for profile, bag and workspace conformance

        Arguments:
            skip_bag (boolean): Whether to skip all checks of manifests and files
            skip_checksums (boolean): Whether to omit checksum checks but still check basic BagIt conformance
            skip_unzip (boolean): Whether the OCRD-ZIP is unzipped, i.e. a directory
            skip_delete (boolean): Whether to skip deleting the unpacked OCRD-ZIP dir after valdiation
            processes (integer): Number of processes used for checksum validation

        """
        if skip_unzip:
            bagdir = self.path_to_zip
            skip_delete = True
        else:
            #  try:
            self.profile_validator.validate_serialization(self.path_to_zip)
            #  except IOError as err:
            #      raise err
            #  except ProfileValidationError as err:
            #      self.report.add_error(err.value)
            bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)
            unzip_file_to_dir(self.path_to_zip, bagdir)


        try:
            bag = Bag(bagdir)
            self._validate_profile(bag)

            if not skip_bag:
                self._validate_bag(bag, fast=skip_checksums, processes=processes)

        finally:
            if not skip_delete:
                # remove tempdir
                rmtree(bagdir)
        return self.report
