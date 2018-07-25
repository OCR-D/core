import json
import re

from jsonschema import Draft4Validator, validators # pylint: disable=import-error

from ocrd.constants import FILE_GROUP_CATEGORIES, FILE_GROUP_PREFIX, OCRD_TOOL_SCHEMA
from ocrd.utils import getLogger

log = getLogger('ocrd.validator')


# http://python-jsonschema.readthedocs.io/en/latest/faq/
def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for prop, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(prop, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return validators.extend(validator_class, {"properties" : set_defaults})


DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)

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

    def __init__(self, schema, validator_class=Draft4Validator):
        self.validator = validator_class(schema)

    def validate(self, obj):
        report = ValidationReport()
        if not self.validator.is_valid(obj):
            for v in self.validator.iter_errors(obj):
                report.add_error("[%s] %s" % ('.'.join(str(vv) for vv in v.path), v.message))
        return report

#
# -------------------------------------------------
#

class ParameterValidator(JsonValidator):

    def __init__(self, ocrd_tool):
        # TODO grep required properties
        required = []
        p = ocrd_tool['parameters']
        for n in p:
            if 'required' in p[n]:
                if p[n]['required']:
                    required.append(n)
                del(p[n]['required'])
        super(ParameterValidator, self).__init__({
            "type": "object",
            "required": required,
            "properties": p
        }, DefaultValidatingDraft4Validator)


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

    def __init__(self, resolver, mets_url, directory=None):
        self.resolver = resolver
        self.mets_url = mets_url
        self.report = ValidationReport()
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
