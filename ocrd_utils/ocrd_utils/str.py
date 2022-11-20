"""
Utility functions for strings, paths and URL.
"""

import re
import json
from .constants import REGEX_FILE_ID

__all__ = [
    'assert_file_grp_cardinality',
    'concat_padded',
    'get_local_filename',
    'is_local_filename',
    'is_string',
    'make_file_id',
    'nth_url_segment',
    'parse_json_string_or_file',
    'parse_json_string_with_comments',
    'remove_non_path_from_url',
    'safe_filename',
]


def assert_file_grp_cardinality(grps, n, msg=None):
    """
    Assert that a string of comma-separated fileGrps contains exactly ``n`` entries.
    """
    if isinstance(grps, str):
        grps = grps.split(',')
    assert len(grps) == n, \
            "Expected exactly %d output file group%s%s, but '%s' has %d" % (
                n,
                '' if n == 1 else 's',
                ' (%s)' % msg if msg else '',
                grps,
                len(grps)
            )

def concat_padded(base, *args):
    """
    Concatenate string and zero-padded 4 digit number
    """
    ret = base
    for n in args:
        if is_string(n):
            ret = "%s_%s" % (ret, n)
        else:
            ret = "%s_%04i"  % (ret, n)
    return ret

def remove_non_path_from_url(url):
    """
    Remove everything from URL after path.
    """
    url = url.split('?', 1)[0]    # query
    url = url.split('#', 1)[0]    # fragment identifier
    url = re.sub(r"/+$", "", url) # trailing slashes
    return url

def make_file_id(ocrd_file, output_file_grp):
    """
    Derive a new file ID for an output file from an existing input file ``ocrd_file``
    and the name of the output file's ``fileGrp/@USE``, ``output_file_grp``.
    If ``ocrd_file``'s ID contains the input file's fileGrp name, then replace it by ``output_file_grp``.
    Else if ``ocrd_file`` has a ``pageId`` but it is not contained in the ``ocrd_file.ID``, then
        concatenate ``output_file_grp`` and ``ocrd_file.pageId``.
    Otherwise concatenate ``output_file_grp`` with the ``ocrd_file.ID``.

    Note: ``make_file_id`` cannot guarantee that the new ID is unique within an actual
    :py:class:`ocrd_models.ocrd_mets.OcrdMets`.
    The caller is responsible for ensuring uniqueness of files to be added.
    Ultimately, ID conflicts will lead to :py:meth:`ocrd_models.ocrd_mets.OcrdMets.add_file`
    raising an exception.
    This can be avoided if all processors use ``make_file_id`` consistently for ID generation.

    Note: ``make_file_id`` generates page-specific IDs. For IDs representing page segments
    or ``pc:AlternativeImage`` files, the output of ``make_file_id`` may need to be concatenated
    with a unique string for that sub-page element, such as `".IMG"` or the segment ID.
    """
    # considerations for this behaviour:
    # - uniqueness (in spite of different METS and processor conventions)
    # - predictability (i.e. output name can be anticipated from the input name)
    # - stability (i.e. output at least as much sorted and consistent as the input)
    # ... and all this in spite of --page-id selection and --overwrite
    # (i.e. --overwrite should target the existing ID, and input vs output
    #  IDs should be different, except when overwriting the input fileGrp)
    ret = ocrd_file.ID.replace(ocrd_file.fileGrp, output_file_grp)
    if ret == ocrd_file.ID and output_file_grp != ocrd_file.fileGrp:
        if ocrd_file.pageId and ocrd_file.pageId not in ocrd_file.ID:
            ret = output_file_grp + '_' + ocrd_file.pageId
        else:
            ret = output_file_grp + '_' + ocrd_file.ID
    if not REGEX_FILE_ID.fullmatch(ret):
        ret = ret.replace(':', '_')
        ret = re.sub(r'^([^a-zA-Z_])', r'id_\1', ret)
        ret = re.sub(r'[^\w.-]', r'', ret)
    return ret

def nth_url_segment(url, n=-1):
    """
    Return the last /-delimited segment of a URL-like string

    Arguments:
        url (string):
        n (integer): index of segment, default: -1
    """
    segments = remove_non_path_from_url(url).split('/')
    try:
        return segments[n]
    except IndexError:
        return ''

def get_local_filename(url, start=None):
    """
    Return local filename, optionally relative to ``start``

    Arguments:
        url (string): filename or URL
        start (string): Base path to remove from filename. Raise an exception if not a prefix of url
    """
    if url.startswith('https://') or url.startswith('http:'):
        raise Exception("Can't determine local filename of http(s) URL")
    if url.startswith('file://'):
        url = url[len('file://'):]
    # Goobi/Kitodo produces those, they are always absolute
    if url.startswith('file:/'):
        url = url[len('file:'):]
    if start:
        if not url.startswith(start):
            raise Exception("Cannot remove prefix %s from url %s" % (start, url))
        if not start.endswith('/'):
            start += '/'
        url = url[len(start):]
    return url

def is_local_filename(url):
    """
    Whether a url is a local filename.
    """
    return url.startswith('file://') or not('://' in url)

def is_string(val):
    """
    Return whether a value is a ``str``.
    """
    return isinstance(val, str)


def parse_json_string_with_comments(val):
    """
    Parse a string of JSON interspersed with #-prefixed full-line comments
    """
    jsonstr = re.sub(r'^\s*#.*$', '', val, flags=re.MULTILINE)
    return json.loads(jsonstr)

def parse_json_string_or_file(*values):    # pylint: disable=unused-argument
    """
    Parse a string as either the path to a JSON object or a literal JSON object.

    Empty strings are equivalent to '{}'
    """
    ret = {}
    for value in values:
        err = None
        value_parsed = None
        if re.fullmatch(r"\s*", value):
            continue
        try:
            try:
                with open(value, 'r') as f:
                    value_parsed = parse_json_string_with_comments(f.read())
            except (FileNotFoundError, OSError):
                value_parsed = parse_json_string_with_comments(value.strip())
            if not isinstance(value_parsed, dict):
                err = ValueError("Not a valid JSON object: '%s' (parsed as '%s')" % (value, value_parsed))
        except json.decoder.JSONDecodeError as e:
            err = ValueError("Error parsing '%s': %s" % (value, e))
        if err:
            raise err       # pylint: disable=raising-bad-type
        ret = {**ret, **value_parsed}
    return ret

def safe_filename(url):
    """
    Sanitize input to be safely used as the basename of a local file.
    """
    ret = re.sub(r'[^\w]+', '_', url)
    ret = re.sub(r'^\.*', '', ret)
    ret = re.sub(r'\.\.*', '.', ret)
    #  print('safe filename: %s -> %s' % (url, ret))
    return ret

def generate_range(start, end):
    """
    Generate a list of strings by incrementing the number part of ``start`` until including ``end``.
    """
    ret = []
    try:
        start_num, end_num = re.findall(r'\d+', start)[-1], re.findall(r'\d+', end)[-1]
    except IndexError:
        raise ValueError("Range '%s..%s': could not find numeric part" % (start, end))
    if start_num == end_num:
        raise ValueError("Range '%s..%s': evaluates to the same number")
    for i in range(int(start_num), int(end_num) + 1):
        ret.append(start.replace(start_num, str(i).zfill(len(start_num))))
    return ret
