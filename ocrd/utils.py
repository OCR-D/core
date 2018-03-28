import subprocess
import logging
import re

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('ocrd.resolver').setLevel(logging.INFO)

UNSAFE_CHARS = r'[^A-Za-z0-9\.]'

def getLogger(*args, **kwargs):
    return logging.getLogger(*args, **kwargs)

def coordinate_string_from_xywh(box):
    """
    Constructs a polygon representation from a rectangle described as a dict with keys x, y, w, h.
    """
    # tesseract uses a different region representation format
    return "%i,%i %i,%i %i,%i %i,%i" % (
        box['x'],
        box['y'],
        box['x'] + box['w'],
        box['y'] + box['w'],
        box['x'] + box['w'] + box['h'],
        box['y'] + box['w'] + box['h'],
        box['x'] + box['h'],
        box['y'] + box['h']
    )

def xywh_from_coordinate_string(points):
    """
    Constructs a numpy-compatible polygon from a page representation.
    """
    polygon = []
    for pair in points.split(" "):
        x_y = pair.split(",")
        polygon.append([float(x_y[0]), float(x_y[1])])
    return polygon

# https://stackoverflow.com/a/10133365/201318
def xmllint_format(xml):
    """
    Format XML by passing it thrugh libxml2's xmllint --format
    """
    proc = subprocess.Popen(
        ['xmllint', '--format', '/dev/stdin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output, _ = proc.communicate(xml)
    return output

def mets_file_id(grp, n):
    """
    Canonical ID of a file within a fileGrp
    """
    return "%s_%04i"  % (grp, n + 1)

def safe_filename(url):
    (basename, ext) = filename_without_extension(url)
    ext = re.sub(UNSAFE_CHARS, '_', ext[1:]) if ext is not None else ''
    return "%s%s" % (
        re.sub(UNSAFE_CHARS, '_', basename),
        ext
    )

def filename_without_extension(fname):
    """
    Return a tuple (filename, extension). Extensions DO include a leading dot.
    """
    ret = fname.rsplit('.', 1)[0]
    if ret.endswith('.tar'):
        ret = ret[0:len(ret)-4]
    return (ret, fname[len(ret):])
