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
    Else if ``ocrd_file``'s ID contains the input file's pageId, then merely append ``output_file_grp``.
    Otherwise use ``output_file_grp`` together with the position of ``ocrd_file`` within the input fileGrp
    (as a fallback counter), and increment counter until there is no more ID conflict.
    """
    ret = ocrd_file.ID.replace(ocrd_file.fileGrp, output_file_grp)
    if ret == ocrd_file.ID:
        if ocrd_file.pageId and ocrd_file.pageId in ocrd_file.ID:
            # still sufficiently unique
            ret = output_file_grp + '_' + ocrd_file.ID
        else:
            ids = [f.ID for f in ocrd_file.mets.find_files(fileGrp=ocrd_file.fileGrp, mimetype=ocrd_file.mimetype)]
            try:
                n = ids.index(ocrd_file.ID) + 1
            except ValueError:
                n = len(ids)
            ret = concat_padded(output_file_grp, n)
            while next(ocrd_file.mets.find_files(ID=ret), None):
                n += 1
                ret = concat_padded(output_file_grp, n)
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
    ret = re.sub(r'[^A-Za-z0-9]+', '.', url)
    ret = re.sub(r'^\.*', '', ret)
    ret = re.sub(r'\.\.*', '.', ret)
    #  print('safe filename: %s -> %s' % (url, ret))
    return ret

def generate_range(start, end):
    """
    Generate a list of strings by incrementing the number part of ``start`` until including ``end``.
    """
    ret = []
    start_num, end_num = re.search(r'\d+', start), re.search(r'\d+', end)
    if not (start_num and end_num):
        raise ValueError("Unable to generate range %s .. %s, could not detect number part" % (start, end))
    start_num, end_num = start_num.group(0), end_num.group(0)
    for i in range(int(start_num), int(end_num) + 1):
        ret.append(start.replace(start_num, str(i).zfill(len(start_num))))
    return ret
