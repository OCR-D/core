"""
Utility methods usable in various circumstances.

* xywh_from_points, points_from_xywh, polygon_from_points

The functions have the syntax X_from_Y, where X/Y can be

points a string encoding a polygon: "0,0 100,0 100,100, 0,100"
polygon an array of x-y-tuples of a polygon: [[0,0], [100,0], [100,100], [0,100]]
xywh a dict with keys for x, y, width and height: {'x': 0, 'y': 0, 'w': 100, 'h': 100}
points is for PAGE

polygon is what opencv2 expects

xywh is what tesserocr expects/produces.
"""

__all__ = [
    'abspath',
    'concat_padded',
    'getLogger',
    'is_local_filename',
    'is_string',
    'logging',
    'points_from_xywh',
    'points_from_x0y0x1y1',
    'polygon_from_points',
    'safe_filename',
    'unzip_file_to_dir',
    'xywh_from_points',

    'VERSION',
    'MIMETYPE_PAGE',
    'EXT_TO_MIME',
]

import re
import sys
import logging
from os.path import isfile, abspath as os_abspath
from zipfile import ZipFile

from .logging import getLogger
from .constants import *  # pylint: disable=wildcard-import

def abspath(url):
    """
    Get a full path to a file or file URL

    See os.abspath
    """
    if url.startswith('file://'):
        url = url[len('file://'):]
    return os_abspath(url)

def concat_padded(base, *args):
    """
    Concatenate string and zero-padded 4 digit number
    """
    ret = base
    for n in args:
        if is_string(n):
            ret = "%s_%s" % (ret, n)
        else:
            ret = "%s_%04i"  % (ret, n + 1)
    return ret

def is_local_filename(url):
    """
    Whether a url is a local filename.
    """
    if url.startswith('file://'):
        return True
    if isfile(url):
        return True
    return False

def is_string(val):
    """
    Return whether a value is a ``str``.
    """
    return isinstance(val, str)

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

def points_from_x0y0x1y1(xyxy):
    """
    Constructs a polygon representation from a rectangle described as a list [x0, y0, x1, y1]
    """
    x0 = xyxy[0]
    y0 = xyxy[1]
    x1 = xyxy[2]
    y1 = xyxy[3]
    return "%s,%s %s,%s %s,%s %s,%s" % (
        x0, y0,
        x1, y0,
        x1, y1,
        x0, y1
    )

def polygon_from_points(points):
    """
    Constructs a numpy-compatible polygon from a page representation.
    """
    polygon = []
    for pair in points.split(" "):
        x_y = pair.split(",")
        polygon.append([float(x_y[0]), float(x_y[1])])
    return polygon

def safe_filename(url):
    """
    Sanitize input to be safely used as the basename of a local file.
    """
    ret = re.sub('[^A-Za-z0-9]+', '.', url)
    #  print('safe filename: %s -> %s' % (url, ret))
    return ret

def unzip_file_to_dir(path_to_zip, output_directory):
    """
    Extract a ZIP archive to a directory
    """
    z = ZipFile(path_to_zip, 'r')
    z.extractall(output_directory)
    z.close()

def xywh_from_points(points):
    """
    Constructs an dict representing a rectangle with keys x, y, w, h
    """
    xys = [[int(p) for p in pair.split(',')] for pair in points.split(' ')]
    minx = sys.maxsize
    miny = sys.maxsize
    maxx = 0
    maxy = 0
    for xy in xys:
        if xy[0] < minx:
            minx = xy[0]
        if xy[0] > maxx:
            maxx = xy[0]
        if xy[1] < miny:
            miny = xy[1]
        if xy[1] > maxy:
            maxy = xy[1]

    return {
        'x': minx,
        'y': miny,
        'w': maxx - minx,
        'h': maxy - miny,
    }
