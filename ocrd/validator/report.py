__all__ = ['ValidationReport']

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
