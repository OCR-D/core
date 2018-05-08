"""
* xywh_from_points, points_from_xywh, polygon_from_points

The functions have the syntax X_from_Y, where X/Y can be

points a string encoding a polygon: "0,0 100,0 100,100, 0,100"
polygon an array of x-y-tuples of a polygon: [[0,0], [100,0], [100,100], [0,100]]
xywh a dict with keys for x, y, width and height: {'x': 0, 'y': 0, 'w': 100, 'h': 100}
points is for PAGE

polygon is what opencv2 expects

xywh is what tesserocr expects/produces.
"""
import subprocess
import logging
import re

logging.basicConfig(level=logging.DEBUG)
#  logging.getLogger('ocrd.resolver').setLevel(logging.INFO)
logging.getLogger('ocrd.resolver.download_to_directory').setLevel(logging.INFO)
logging.getLogger('ocrd.resolver.add_files_to_mets').setLevel(logging.INFO)

def getLogger(*args, **kwargs):
    return logging.getLogger(*args, **kwargs)

def points_from_xywh(box):
    """
    Constructs a polygon representation from a rectangle described as a dict with keys x, y, w, h.
    """
    x, y, w, h = box['x'], box['y'], box['w'], box['h']
    # tesseract uses a different region representation format
    return "%i,%i %i,%i %i,%i %i,%i" % (
        x, y,
        x + w, y,
        x + w, y + h,
        x, y + h
    )

def xywh_from_points(points):
    """
    Constructs an dict representing a rectangle with keys x, y, w, h
    """
    [tl, tr, br] = [[int(p) for p in pair.split(',')] for pair in points.split(' ')[:3]]
    return {
        'x': tl[0],
        'y': tl[1],
        'w': tr[0] - tl[0],
        'h': br[1] - tr[1],
    }

def polygon_from_points(points):
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
    proc = subprocess.Popen(
        ['xmllint', '--format', '/dev/stdin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output, _ = proc.communicate(xml)
    return output

# TODO better name
def mets_file_id(grp, n):
    """
    Concatenate string and zero-padded 4 digit number
    """
    return "%s_%04i"  % (grp, n + 1)

def safe_filename(url):
    ret = re.sub('[^A-Za-z0-9]', '', url)
    return ret
