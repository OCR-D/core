import json
import re

import jsonschema # pylint: disable=import-error

from ocrd.constants import FILE_GROUP_CATEGORIES, FILE_GROUP_PREFIX, OCRD_TOOL_SCHEMA
from ocrd.utils import getLogger

log = getLogger('ocrd.validator')

#
# -------------------------------------------------
#

class ValidationReport(object):
    """
    Container of warnings and errors about a workspace.
    """

    def __init__(self):
        self.entries = []
        self.warnings = []
        self.errors = []

    def __str__(self):
        ret = 'OK' if self.is_valid else 'INVALID'
        if not self.is_valid:
            ret += '['
            if self.warnings:
                ret += ' %s warnings' % len(self.warnings)
            if self.errors:
                ret += ' %s errors' % len(self.errors)
            ret += ' ]'
        return ret

    @property
    def is_valid(self):
        return not self.warnings and not self.errors

    def to_xml(self):
        body = ''
        for k in ['warning', 'error']:
            for msg in self.__dict__[k + 's']:
                body += '\n  <%s>%s</%s>' % (k, msg, k)
        return '<report valid="%s">%s\n</report>' % ("true" if self.is_valid else "false", body)

    def add_warning(self, msg):
        self.warnings.append(msg)

    def add_error(self, msg):
        self.errors.append(msg)

#
# -------------------------------------------------
#

class JsonValidator(object):

    @staticmethod
    def validate_json(obj, schema):
        if isinstance(obj, str):
            obj = json.loads(obj)
        return JsonValidator(schema).validate(obj)

    def __init__(self, schema):
        self.validator = jsonschema.Draft4Validator(schema)

    def validate(self, cli_json):
        report = ValidationReport()
        if not self.validator.is_valid(cli_json):
            for v in self.validator.iter_errors(cli_json):
                report.add_error("[%s] %s" % ('.'.join(str(vv) for vv in v.path), v.message))
        return report

#
# -------------------------------------------------
#

#  # TODO Implement

#  class ParameterValidator(object):
#      """
#      Validates parameters against an ``ocrd-tool.json`` schema.
#      """

#      def __init__(self, ocrd_tool):
#          self.validator = JsonValidator(ocrd_tool['parameter'])

#
# -------------------------------------------------
#

class OcrdToolValidator(JsonValidator):

    @staticmethod
    def validate_json(obj, schema=OCRD_TOOL_SCHEMA):
        return JsonValidator.validate_json(obj, schema)

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

    def __init__(self, resolver, mets_url):
        self.resolver = resolver
        self.mets_url = mets_url
        self.report = ValidationReport()
        self.workspace = self.resolver.workspace_from_url(mets_url)
        self.mets = self.workspace.mets

    @staticmethod
    def validate_url(resolver, mets_url):
        """
        Validates the workspace of a METS URL against the specs

        Returns:
            report (:class:`ValidationReport`) Report on the validity
        """
        validator = WorkspaceValidator(resolver, mets_url)
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
        for f in self.mets.find_files(mimetype='image/tif'):
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
