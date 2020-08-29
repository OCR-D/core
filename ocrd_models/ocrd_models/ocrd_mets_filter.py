from re import fullmatch
from ocrd_utils import REGEX_PREFIX, getLogger

LOG = getLogger('ocrd.models.ocrd_mets_filter')

FIELDS = ['fileGrp', 'pageId', 'mimetype', 'ID']
FIELDS_INCLUDE = ['%s_include' % f for f in FIELDS]
FIELDS_EXCLUDE = ['%s_exclude' % f for f in FIELDS]
SYNONYMS = {
    'filegrp': 'fileGrp',
    'file_grp': 'fileGrp',
    'pageid': 'pageId',
    'page_id': 'pageId',
    'id': 'ID',
    'file_id': 'ID',
}

class OcrdMetsFilter():
    """
    Define file restrictions on mets:files
    """

    def __init__(self, **kwargs):
        for attr in FIELDS_INCLUDE + FIELDS_EXCLUDE:
            setattr(self, attr, None)
        for k in kwargs:
            field, include_or_exclude = k.split('_', 2) if k.endswith('clude') else (k, 'include')
            field = SYNONYMS.get(field, field)
            if field not in FIELDS:
                raise ValueError("Unrecognized filter option: %s" % k)
            setattr(self, '%s_%s' % (field, include_or_exclude), kwargs[k])

    def __str__(self):
        ret = []
        for n, field in enumerate(FIELDS):
            if getattr(self, FIELDS_INCLUDE[n]):
                ret.append('%s==%s' % (field, getattr(self, FIELDS_INCLUDE[n])))
            if getattr(self, FIELDS_EXCLUDE[n]):
                ret.append('%s!=%s' % (field, getattr(self, FIELDS_EXCLUDE[n])))
        return 'OcrdMetsFilter(%s)' % (' and '.join(ret))

    def _equals_or_regex_matches(self, val, needle):
        # XXX string comparison only
        val = str(val)
        if needle.startswith(REGEX_PREFIX):
            return fullmatch(needle[len(REGEX_PREFIX):], val)
        return val == needle

    def _file_is_excluded(self, ocrd_file):
        for n, field in enumerate(FIELDS):
            needle = getattr(self, FIELDS_EXCLUDE[n])
            if not needle:
                continue
            val = getattr(ocrd_file, field)
            if not val:
                continue
            if isinstance(needle, list):
                if any(self._equals_or_regex_matches(val, k) for k in needle):
                    return True
            else:
                if self._equals_or_regex_matches(val, needle):
                    return True

    def find_files(self, mets):
        """
        Translate OcrdMetsFilter into a OcrdMets.find_files query

        Args:
            mets (OcrdMets|Workspace): OcrdMets or Workspace wrapping OcrdMets
        """
        LOG.info('Filtering METS with %s' % self)
        if hasattr(mets, 'mets'):
            mets = mets.mets
        files = []
        include_args = {field:getattr(self, FIELDS_INCLUDE[n]) for n, field in enumerate(FIELDS)}
        LOG.info("find_files args: %s" % include_args)
        for ocrd_file in mets.find_files(**include_args):
            if self._file_is_excluded(ocrd_file):
                continue
            files.append(ocrd_file)
        return files
