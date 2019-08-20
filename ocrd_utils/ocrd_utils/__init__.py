"""
Utility methods usable in various circumstances.

* ``coordinates_of_segment``, ``coordinates_for_segment``, ``rotate_coordinates``, ``xywh_from_points``, ``points_from_xywh``, ``polygon_from_points``

These functions convert polygon outlines for PAGE elements on all hierarchy
levels (page, region, line, word, glyph) between relative coordinates w.r.t.
parent segment and absolute coordinates w.r.t. the top-level (source) image.
This includes rotation and offset correction.

* ``polygon_mask``, ``image_from_polygon``, ``crop_image``

These functions combine PIL.Image with polygons or bboxes.
The functions have the syntax ``X_from_Y``, where ``X``/``Y`` can be

    * ``bbox`` is a 4-tuple of integers x0, y0, x1, y1 of the bounding box (rectangle)
    * ``points`` a string encoding a polygon: ``"0,0 100,0 100,100, 0,100"``
    * ``polygon`` is a list of 2-lists of integers x, y of points forming an (implicitly closed) polygon path: ``[[0,0], [100,0], [100,100], [0,100]]``
    * ``xywh`` a dict with keys for x, y, width and height: ``{'x': 0, 'y': 0, 'w': 100, 'h': 100}``
    * ``x0y0x1y1`` is a 4-list of strings ``x0``, ``y0``, ``x1``, ``y1`` of the bounding box (rectangle)
    * ``y0x0y1x1`` is the same as ``x0y0x1y1`` with positions of ``x`` and ``y`` in the list swapped

``polygon`` is what opencv2 and higher-level coordinate functions in ocrd_utils expect

``xywh`` and ``x0y0x1y1`` are what tesserocr expects/produces.

``points`` is what PAGE-XML uses.

``bbox`` is what PIL.Image uses.

* ``is_local_filename``, ``safe_filename``, ``abspath``

FS-related utilities

* ``is_string``, ``membername``, ``concat_padded``

String and OOP utilities

* ``MIMETYPE_PAGE``, ``EXT_TO_MIME``, ``VERSION``

Constants
"""

__all__ = [
    'abspath',
    'bbox_from_points',
    'bbox_from_xywh',
    'bbox_from_polygon',
    'coordinates_for_segment',
    'coordinates_of_segment',
    'concat_padded',
    'crop_image',
    'getLogger',
    'is_local_filename',
    'is_string',
    'logging',
    'membername',
    'image_from_polygon',
    'points_from_bbox',
    'points_from_polygon',
    'points_from_x0y0x1y1',
    'points_from_xywh',
    'points_from_y0x0y1x1',
    'polygon_from_bbox',
    'polygon_from_points',
    'polygon_from_x0y0x1y1',
    'polygon_from_xywh',
    'polygon_mask',
    'rotate_coordinates',
    'safe_filename',
    'unzip_file_to_dir',
    'xywh_from_bbox',
    'xywh_from_points',

    'VERSION',
    'MIMETYPE_PAGE',
    'EXT_TO_MIME',
]

import io
import re
import sys
import logging
import os
from os import getcwd, chdir
from os.path import isfile, abspath as os_abspath
from zipfile import ZipFile
import contextlib

import numpy as np
from PIL import Image, ImageStat, ImageDraw

import logging
from .logging import getLogger
from .constants import *  # pylint: disable=wildcard-import

LOG = getLogger('ocrd_utils')


def abspath(url):
    """
    Get a full path to a file or file URL

    See os.abspath
    """
    if url.startswith('file://'):
        url = url[len('file://'):]
    return os_abspath(url)

def bbox_from_points(points):
    """Construct a numeric list representing a bounding box from polygon coordinates in page representation."""
    xys = [[int(p) for p in pair.split(',')] for pair in points.split(' ')]
    return bbox_from_polygon(xys)

def bbox_from_polygon(polygon):
    """Construct a numeric list representing a bounding box from polygon coordinates in numeric list representation."""
    minx = sys.maxsize
    miny = sys.maxsize
    maxx = 0
    maxy = 0
    for xy in polygon:
        if xy[0] < minx:
            minx = xy[0]
        if xy[0] > maxx:
            maxx = xy[0]
        if xy[1] < miny:
            miny = xy[1]
        if xy[1] > maxy:
            maxy = xy[1]
    return minx, miny, maxx, maxy

def bbox_from_xywh(xywh):
    """Convert a bounding box from a numeric dict to a numeric list representation."""
    return (
        xywh['x'],
        xywh['y'],
        xywh['x'] + xywh['w'],
        xywh['y'] + xywh['h']
    )

def xywh_from_polygon(polygon):
    """Construct a numeric dict representing a bounding box from polygon coordinates in numeric list representation."""
    return xywh_from_bbox(*bbox_from_polygon(polygon))

def coordinates_for_segment(polygon, parent_image, parent_xywh):
    """Convert a relative coordinates polygon to absolute.

    Given a numpy array ``polygon`` of points, and a parent PIL.Image
    along with its bounding box to which the coordinates are relative,
    calculate the absolute coordinates within the page.
    That is, (in case the parent was rotated,) rotate all points in
    opposite direction with the center of the image as origin, then
    shift all points to the offset of the parent.

    Return the rounded numpy array of the resulting polygon.
    """
    # angle correction (unrotate coordinates if image has been rotated):
    if 'angle' in parent_xywh:
        polygon = rotate_coordinates(
            polygon, -parent_xywh['angle'],
            orig=np.array([0.5 * parent_image.width,
                           0.5 * parent_image.height]))
    # offset correction (shift coordinates from base of segment):
    polygon += np.array([parent_xywh['x'], parent_xywh['y']])
    return np.round(polygon).astype(np.int32)

def coordinates_of_segment(segment, parent_image, parent_xywh):
    """Extract the relative coordinates polygon of a PAGE segment element.

    Given a Region / TextLine / Word / Glyph ``segment`` and
    the PIL.Image of its parent Page / Region / TextLine / Word
    along with its bounding box, calculate the relative coordinates
    of the segment within the image. That is, shift all points from
    the offset of the parent, and (in case the parent was rotated,)
    rotate all points with the center of the image as origin.

    Return the rounded numpy array of the resulting polygon.
    """
    # get polygon:
    polygon = np.array(polygon_from_points(segment.get_Coords().points))
    # offset correction (shift coordinates to base of segment):
    polygon -= np.array([parent_xywh['x'], parent_xywh['y']])
    # angle correction (rotate coordinates if image has been rotated):
    if 'angle' in parent_xywh:
        polygon = rotate_coordinates(
            polygon, parent_xywh['angle'],
            orig=np.array([0.5 * parent_image.width,
                           0.5 * parent_image.height]))
    return np.round(polygon).astype(np.int32)

@contextlib.contextmanager
def pushd_popd(newcwd=None):
    oldcwd = getcwd()
    try:
        if newcwd:
            chdir(newcwd)
        yield
    finally:
        chdir(oldcwd)

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

def crop_image(image, box=None):
    """"Crop an image to a rectangle, filling with background.

    Given a PIL.Image ``image`` and a list ``box`` of the bounding
    rectangle relative to the image, crop at the box coordinates,
    filling everything outside ``image`` with the background.
    (This covers the case where ``box`` indexes are negative or
    larger than ``image`` width/height. PIL.Image.crop would fill
    with black.) Since ``image`` is not necessarily binarized yet,
    determine the background from the median color (instead of
    white).

    Return a new PIL.Image.
    """
    # todo: perhaps we should issue a warning if we encounter this
    # (It should be invalid in PAGE-XML to extend beyond parents.)
    if not box:
        box = (0, 0, image.width, image.height)
    xywh = xywh_from_bbox(*box)
    background = ImageStat.Stat(image).median[0]
    new_image = Image.new(image.mode, (xywh['w'], xywh['h']),
                          background) # or 'white'
    new_image.paste(image, (-xywh['x'], -xywh['y']))
    return new_image

def image_from_polygon(image, polygon):
    """"Mask an image with a polygon.

    Given a PIL.Image ``image`` and a numpy array ``polygon``
    of relative coordinates into the image, put everything
    outside the polygon hull to the background. Since ``image``
    is not necessarily binarized yet, determine the background
    from the median color (instead of white).

    Return a new PIL.Image.
    """
    mask = polygon_mask(image, polygon)
    # create a background image from its median color
    # (in case it has not been binarized yet):
    # array = np.asarray(image)
    # background = np.median(array, axis=[0, 1], keepdims=True)
    # array = np.broadcast_to(background.astype(np.uint8), array.shape)
    background = ImageStat.Stat(image).median[0]
    new_image = Image.new('L', image.size, background)
    new_image.paste(image, mask=mask)
    return new_image

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

def membername(class_, val):
    """Convert a member variable/constant into a member name string."""
    return next((k for k, v in class_.__dict__.items() if v == val), str(val))

def points_from_bbox(minx, miny, maxx, maxy):
    """Construct polygon coordinates in page representation from a numeric list representing a bounding box."""
    return "%i,%i %i,%i %i,%i %i,%i" % (
        minx, miny, maxx, miny, maxx, maxy, minx, maxy)

def points_from_polygon(polygon):
    """Convert polygon coordinates from a numeric list representation to a page representation."""
    return " ".join("%i,%i" % (x, y) for x, y in polygon)

def points_from_xywh(box):
    """
    Construct polygon coordinates in page representation from numeric dict representing a bounding box.
    """
    x, y, w, h = box['x'], box['y'], box['w'], box['h']
    # tesseract uses a different region representation format
    return "%i,%i %i,%i %i,%i %i,%i" % (
        x, y,
        x + w, y,
        x + w, y + h,
        x, y + h
    )

def points_from_y0x0y1x1(yxyx):
    """
    Construct a polygon representation from a rectangle described as a list [y0, x0, y1, x1]
    """
    y0 = yxyx[0]
    x0 = yxyx[1]
    y1 = yxyx[2]
    x1 = yxyx[3]
    return "%s,%s %s,%s %s,%s %s,%s" % (
        x0, y0,
        x1, y0,
        x1, y1,
        x0, y1
    )

def points_from_x0y0x1y1(xyxy):
    """
    Construct a polygon representation from a rectangle described as a list [x0, y0, x1, y1]
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

def polygon_from_bbox(minx, miny, maxx, maxy):
    """Construct polygon coordinates in numeric list representation from a numeric list representing a bounding box."""
    return [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]]

def polygon_from_points(points):
    """
    Convert polygon coordinates in page representation to polygon coordinates in numeric list representation.
    """
    polygon = []
    for pair in points.split(" "):
        x_y = pair.split(",")
        polygon.append([float(x_y[0]), float(x_y[1])])
    return polygon

def polygon_from_x0y0x1y1(x0y0x1y1):
    """Construct polygon coordinates in numeric list representation from a string list representing a bounding box."""
    minx = int(x0y0x1y1[0])
    miny = int(x0y0x1y1[1])
    maxx = int(x0y0x1y1[2])
    maxy = int(x0y0x1y1[3])
    return [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]]

def polygon_from_xywh(xywh):
    """Construct polygon coordinates in numeric list representation from numeric dict representing a bounding box."""
    return polygon_from_bbox(*bbox_from_xywh(xywh))

def polygon_mask(image, coordinates):
    """"Create a mask image of a polygon.

    Given a PIL.Image ``image`` (merely for dimensions), and
    a numpy array ``polygon`` of relative coordinates into the image,
    create a new image of the same size with black background, and
    fill everything inside the polygon hull with white.

    Return the new PIL.Image.
    """
    mask = Image.new('L', image.size, 0)
    if isinstance(coordinates, np.ndarray):
        coordinates = list(map(tuple, coordinates))
    ImageDraw.Draw(mask).polygon(coordinates, outline=1, fill=255)
    return mask

def rotate_coordinates(polygon, angle, orig=np.array([0, 0])):
    """Apply a passive rotation transformation to the given coordinates.

    Given a numpy array ``polygon`` of points and a rotation ``angle``,
    as well as a numpy array ``orig`` of the center of rotation,
    calculate the coordinate transform corresponding to the rotation
    of the underlying image by ``angle`` degrees at ``center`` by
    applying translation to the center, inverse rotation,
    and translation from the center.

    Return a numpy array of the resulting polygon.
    """
    angle = np.deg2rad(angle)  # pylint: disable=assignment-from-no-return
    cos = np.cos(angle)
    sin = np.sin(angle)
    # active rotation:  [[cos, -sin], [sin, cos]]
    # passive rotation: [[cos, sin], [-sin, cos]] (inverse)
    return orig + np.dot(polygon - orig, np.array([[cos, sin], [-sin, cos]]).transpose())

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

def xywh_from_bbox(minx, miny, maxx, maxy):
    """Convert a bounding box from a numeric list to a numeric dict representation."""
    return {
        'x': minx,
        'y': miny,
        'w': maxx - minx,
        'h': maxy - miny,
    }

def xywh_from_points(points):
    """
    Construct a numeric dict representing a bounding box from polygon coordinates in page representation.
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
