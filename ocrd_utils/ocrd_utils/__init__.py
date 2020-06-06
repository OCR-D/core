"""
Utility functions and constants usable in various circumstances.

* ``coordinates_of_segment``, ``coordinates_for_segment``

    These functions convert polygon outlines for PAGE elements on all hierarchy
    levels below page (i.e. region, line, word, glyph) between relative coordinates
    w.r.t. a corresponding image and absolute coordinates w.r.t. the top-level image.
    This includes rotation and offset correction, based on affine transformations.
    (Used by ``Workspace`` methods ``image_from_page`` and ``image_from_segment``)

* ``rotate_coordinates``, ``shift_coordinates``, ``transpose_coordinates``, ``transform_coordinates``

    These backend functions compose affine transformations for reflection, rotation
    and offset correction of coordinates, or apply them to a set of points. They can be
    used to pass down the coordinate system along with images (both invariably sharing
    the same operations context) when traversing the element hierarchy top to bottom.
    (Used by ``Workspace`` methods ``image_from_page`` and ``image_from_segment``).

* ``rotate_image``, ``crop_image``, ``transpose_image``

    These PIL.Image functions are safe replacements for the ``rotate``, ``crop``, and
    ``transpose`` methods.

* ``image_from_polygon``, ``polygon_mask``

    These functions apply polygon masks to PIL.Image objects.

* ``xywh_from_points``, ``points_from_xywh``, ``polygon_from_points`` etc.

   These functions have the syntax ``X_from_Y``, where ``X``/``Y`` can be

    * ``bbox`` is a 4-tuple of integers x0, y0, x1, y1 of the bounding box (rectangle)

      (used by PIL.Image)
    * ``points`` a string encoding a polygon: ``"0,0 100,0 100,100, 0,100"``

      (used by PAGE-XML)
    * ``polygon`` is a list of 2-lists of integers x, y of points forming an (implicitly closed) polygon path: ``[[0,0], [100,0], [100,100], [0,100]]``

      (used by opencv2 and higher-level coordinate functions in ocrd_utils)
    * ``xywh`` a dict with keys for x, y, width and height: ``{'x': 0, 'y': 0, 'w': 100, 'h': 100}``

      (produced by tesserocr and image/coordinate recursion methods in ocrd.workspace)
    * ``x0y0x1y1`` is a 4-list of strings ``x0``, ``y0``, ``x1``, ``y1`` of the bounding box (rectangle)

      (produced by tesserocr)
    * ``y0x0y1x1`` is the same as ``x0y0x1y1`` with positions of ``x`` and ``y`` in the list swapped

* ``is_local_filename``, ``safe_filename``, ``abspath``, ``get_local_filename``

    FS-related utilities

* ``is_string``, ``membername``, ``concat_padded``, ``nth_url_segment``, ``remove_non_path_from_url``, ``parse_json_string_or_file``

    String and OOP utilities

* ``MIMETYPE_PAGE``, ``EXT_TO_MIME``, ``MIME_TO_EXT``, ``VERSION``

    Constants

* ``logging``, ``setOverrideLogLevel``, ``getLevelName``, ``getLogger``, ``initLogging``

    Exports of ocrd_utils.logging

* ``deprecated_alias``

    Decorator to mark a kwarg as deprecated
"""

__all__ = [
    'abspath',
    'adjust_canvas_to_rotation',
    'adjust_canvas_to_transposition',
    'bbox_from_points',
    'bbox_from_xywh',
    'bbox_from_polygon',
    'coordinates_for_segment',
    'coordinates_of_segment',
    'concat_padded',
    'crop_image',
    'deprecated_alias',
    'getLevelName',
    'getLogger',
    'initLogging',
    'is_local_filename',
    'is_string',
    'nth_url_segment',
    'remove_non_path_from_url',
    'logging',
    'membername',
    'image_from_polygon',
    'parse_json_string_or_file',
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
    'rotate_image',
    'safe_filename',
    'setOverrideLogLevel',
    'shift_coordinates',
    'transform_coordinates',
    'transpose_coordinates',
    'transpose_image',
    'unzip_file_to_dir',
    'xywh_from_bbox',
    'xywh_from_points',

    'VERSION',
    'MIMETYPE_PAGE',
    'EXT_TO_MIME',
    'MIME_TO_EXT',
]

import io
import json
import sys
import os
from os import getcwd, chdir
from os.path import isfile, abspath as os_abspath
import re
from zipfile import ZipFile
import contextlib

import numpy as np
from PIL import Image, ImageStat, ImageDraw, ImageChops

from .logging import * # pylint: disable=wildcard-import
from .constants import *  # pylint: disable=wildcard-import
from .deprecate import deprecated_alias

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
    maxx = -sys.maxsize
    maxy = -sys.maxsize
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

def coordinates_for_segment(polygon, parent_image, parent_coords):
    """Convert relative coordinates to absolute.

    Given...

    - ``polygon``, a numpy array of points relative to
    - ``parent_image``, a PIL.Image (not used), along with
    - ``parent_coords``, its corresponding affine transformation,

    ...calculate the absolute coordinates within the page.
    
    That is, apply the given transform inversely to ``polygon``
    The transform encodes (recursively):

    1. Whenever ``parent_image`` or any of its parents was cropped,
       all points must be shifted by the offset in opposite direction
       (i.e. coordinate system gets translated by the upper left).
    2. Whenever ``parent_image`` or any of its parents was rotated,
       all points must be rotated around the center of that image in
       opposite direction
       (i.e. coordinate system gets translated by the center in
       opposite direction, rotated purely, and translated back;
       the latter involves an additional offset from the increase
       in canvas size necessary to accommodate all points).

    Return the rounded numpy array of the resulting polygon.
    """
    polygon = np.array(polygon, dtype=np.float32) # avoid implicit type cast problems
    # apply inverse of affine transform:
    inv_transform = np.linalg.inv(parent_coords['transform'])
    polygon = transform_coordinates(polygon, inv_transform)
    return np.round(polygon).astype(np.int32)

def coordinates_of_segment(segment, parent_image, parent_coords):
    """Extract the coordinates of a PAGE segment element relative to its parent.

    Given...

    - ``segment``, a PAGE segment object in absolute coordinates
      (i.e. RegionType / TextLineType / WordType / GlyphType), and
    - ``parent_image``, the PIL.Image of its corresponding parent object
      (i.e. PageType / RegionType / TextLineType / WordType), (not used),
      along with
    - ``parent_coords``, its corresponding affine transformation,

    ...calculate the relative coordinates of the segment within the image.

    That is, apply the given transform to the points annotated in ``segment``.
    The transform encodes (recursively):

    1. Whenever ``parent_image`` or any of its parents was cropped,
       all points must be shifted by the offset
       (i.e. coordinate system gets translated by the upper left).
    2. Whenever ``parent_image`` or any of its parents was rotated,
       all points must be rotated around the center of that image
       (i.e. coordinate system gets translated by the center in
       opposite direction, rotated purely, and translated back;
       the latter involves an additional offset from the increase
       in canvas size necessary to accommodate all points).

    Return the rounded numpy array of the resulting polygon.
    """
    # get polygon:
    polygon = np.array(polygon_from_points(segment.get_Coords().points))
    # apply affine transform:
    polygon = transform_coordinates(polygon, parent_coords['transform'])
    return np.round(polygon).astype(np.int32)

@contextlib.contextmanager
def pushd_popd(newcwd=None):
    try:
        oldcwd = getcwd()
    except FileNotFoundError as e:  # pylint: disable=unused-variable
        # This happens when a directory is deleted before the context is exited
        oldcwd = '/tmp'
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

def remove_non_path_from_url(url):
    """
    Remove everything from URL after path.
    """
    url = url.split('?', 1)[0]    # query
    url = url.split('#', 1)[0]    # fragment identifier
    url = re.sub(r"/+$", "", url) # trailing slashes
    return url

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
    if not box:
        box = (0, 0, image.width, image.height)
    elif box[0] < 0 or box[1] < 0 or box[2] > image.width or box[3] > image.height:
        # (It should be invalid in PAGE-XML to extend beyond parents.)
        LOG.warning('crop coordinates (%s) exceed image (%dx%d)',
                    str(box), image.width, image.height)
    LOG.debug('cropping image to %s', str(box))
    xywh = xywh_from_bbox(*box)
    background = tuple(ImageStat.Stat(image).median)
    new_image = Image.new(image.mode, (xywh['w'], xywh['h']),
                          background) # or 'white'
    new_image.paste(image, (-xywh['x'], -xywh['y']))
    return new_image

def rotate_image(image, angle, fill='background', transparency=False):
    """"Rotate an image, enlarging and filling with background.

    Given a PIL.Image ``image`` and a rotation angle in degrees
    counter-clockwise ``angle``, rotate the image, increasing its
    size at the margins accordingly, and filling everything outside
    the original image according to ``fill``:

    - if ``background`` (the default),
      then use the median color of the image;
    - otherwise use the given color, e.g. ``'white'`` or (255,255,255).

    Moreover, if ``transparency`` is true, then add an alpha channel
    fully opaque (i.e. everything outside the original image will
    be transparent for those that can interpret alpha channels).
    (This is true for images which already have an alpha channel,
    regardless of the setting used.)

    Return a new PIL.Image.
    """
    LOG.debug('rotating image by %.2f°', angle)
    if transparency and image.mode in ['RGB', 'L']:
        # ensure no information is lost by adding transparency channel
        # initialized to fully opaque (so cropping and rotation will
        # expose areas as transparent):
        image = image.copy()
        image.putalpha(255)
    if fill == 'background':
        background = ImageStat.Stat(image).median
        if image.mode in ['RGBA', 'LA']:
            background[-1] = 0 # fully transparent
        background = tuple(background)
    else:
        background = fill
    new_image = image.rotate(angle,
                             expand=True,
                             #resample=Image.BILINEAR,
                             fillcolor=background)
    if new_image.mode in ['LA']:
        # workaround for #1600 (bug in LA support which
        # causes areas fully transparent before rotation
        # to be filled with black here):
        image = new_image
        new_image = Image.new(image.mode, image.size, background)
        new_image.paste(image, mask=image.getchannel('A'))
    return new_image

def transpose_image(image, method):
    """"Transpose (i.e. flip or rotate in 90° multiples) an image.

    Given a PIL.Image ``image`` and a transposition mode ``method``,
    apply the respective operation:

    - ``PIL.Image.FLIP_LEFT_RIGHT``:
      all pixels get mirrored at half the width of the image
    - ``PIL.Image.FLIP_TOP_BOTTOM``:
      all pixels get mirrored at half the height of the image
    - ``PIL.Image.ROTATE_180``:
      all pixels get mirrored at both, the width and half the height
      of the image,
      i.e. the image gets rotated by 180° counter-clockwise
    - ``PIL.Image.ROTATE_90``:
      rows become columns (but counted from the right) and
      columns become rows,
      i.e. the image gets rotated by 90° counter-clockwise;
      width becomes height and vice versa
    - ``PIL.Image.ROTATE_270``:
      rows become columns and
      columns become rows (but counted from the bottom),
      i.e. the image gets rotated by 270° counter-clockwise;
      width becomes height and vice versa
    - ``PIL.Image.TRANSPOSE``:
      rows become columns and vice versa,
      i.e. all pixels get mirrored at the main diagonal;
      width becomes height and vice versa
    - ``PIL.Image.TRANSVERSE``:
      rows become columns (but counted from the right) and
      columns become rows (but counted from the bottom),
      i.e. all pixels get mirrored at the opposite diagonal;
      width becomes height and vice versa
    
    Return a new PIL.Image.
    """
    LOG.debug('transposing image with %s', membername(Image, method))
    return image.transpose(method)
    
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
        raise Exception("Invalid (java) URL: %s" % url)
    if start:
        if not url.startswith(start):
            raise Exception("Cannot remove prefix %s from url %s" % (start, url))
        if not start.endswith('/'):
            start += '/'
        url = url[len(start):]
    return url

def image_from_polygon(image, polygon, fill='background', transparency=False):
    """"Mask an image with a polygon.

    Given a PIL.Image ``image`` and a numpy array ``polygon``
    of relative coordinates into the image, fill everything
    outside the polygon hull to a color according to ``fill``:

    - if ``background`` (the default),
      then use the median color of the image;
    - otherwise use the given color, e.g. ``'white'`` or (255,255,255).

    Moreover, if ``transparency`` is true, then add an alpha channel
    from the polygon mask (i.e. everything outside the polygon will
    be transparent, for those consumers that can interpret alpha channels).
    Images which already have an alpha channel will have it shrunk
    from the polygon mask (i.e. everything outside the polygon will
    be transparent, in addition to existing transparent pixels).
    
    Return a new PIL.Image.
    """
    mask = polygon_mask(image, polygon)
    if fill == 'background':
        background = tuple(ImageStat.Stat(image).median)
    else:
        background = fill
    new_image = Image.new(image.mode, image.size, background)
    new_image.paste(image, mask=mask)
    # ensure no information is lost by a adding transparency channel
    # initialized to fully transparent outside the polygon mask
    # (so consumers do not have to rely on background estimation,
    #  which can fail on foreground-dominated segments, or white,
    #  which can be inconsistent on unbinarized images):
    if image.mode in ['RGBA', 'LA']:
        # ensure transparency maximizes (i.e. parent mask AND mask):
        mask = ImageChops.darker(mask, image.getchannel('A')) # min opaque
        new_image.putalpha(mask)
    elif transparency and image.mode in ['RGB', 'L']:
        # introduce transparency:
        new_image.putalpha(mask)
    return new_image

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
    ImageDraw.Draw(mask).polygon(coordinates, outline=255, fill=255)
    return mask

def adjust_canvas_to_rotation(size, angle):
    """Calculate the enlarged image size after rotation.
    
    Given a numpy array ``size`` of an original canvas (width and height),
    and a rotation angle in degrees counter-clockwise ``angle``,
    calculate the new size which is necessary to encompass the full
    image after rotation.
    
    Return a numpy array of the enlarged width and height.
    """
    angle = np.deg2rad(angle)
    sin = np.abs(np.sin(angle))
    cos = np.abs(np.cos(angle))
    return np.dot(np.array([[cos, sin],
                            [sin, cos]]),
                  np.array(size))

def adjust_canvas_to_transposition(size, method):
    """Calculate the flipped image size after transposition.
    
    Given a numpy array ``size`` of an original canvas (width and height),
    and a transposition mode ``method`` (see ``transpose_image``),
    calculate the new size after transposition.
    
    Return a numpy array of the enlarged width and height.
    """
    if method in [Image.ROTATE_90,
                  Image.ROTATE_270,
                  Image.TRANSPOSE,
                  Image.TRANSVERSE]:
        size = size[::-1]
    return size

def rotate_coordinates(transform, angle, orig=np.array([0, 0])):
    """Compose an affine coordinate transformation with a passive rotation.

    Given a numpy array ``transform`` of an existing transformation
    matrix in homogeneous (3d) coordinates, and a rotation angle in
    degrees counter-clockwise ``angle``, as well as a numpy array
    ``orig`` of the center of rotation, calculate the affine
    coordinate transform corresponding to the composition of both
    transformations. (This entails translation to the center, followed
    by pure rotation, and subsequent translation back. However, since
    rotation necessarily increases the bounding box, and thus image size,
    do not translate back the same amount, but to the enlarged offset.)
    
    Return a numpy array of the resulting affine transformation matrix.
    """
    LOG.debug('rotating coordinates by %.2f° around %s', angle, str(orig))
    rad = np.deg2rad(angle)
    cos = np.cos(rad)
    sin = np.sin(rad)
    # get rotation matrix for passive rotation:
    rot = np.array([[+cos, sin, 0],
                    [-sin, cos, 0],
                    [0, 0, 1]])
    return shift_coordinates(
        np.dot(rot,
               shift_coordinates(transform,
                                 -orig)),
        #orig)
        # the image (bounding box) increases with rotation,
        # so we must translate back to the new upper left:
        adjust_canvas_to_rotation(orig, angle))

def shift_coordinates(transform, offset):
    """Compose an affine coordinate transformation with a translation.

    Given a numpy array ``transform`` of an existing transformation
    matrix in homogeneous (3d) coordinates, and a numpy array
    ``offset`` of the translation vector, calculate the affine
    coordinate transform corresponding to the composition of both
    transformations.
    
    Return a numpy array of the resulting affine transformation matrix.
    """
    LOG.debug('shifting coordinates by %s', str(offset))
    shift = np.eye(3)
    shift[0, 2] = offset[0]
    shift[1, 2] = offset[1]
    return np.dot(shift, transform)

def transpose_coordinates(transform, method, orig=np.array([0, 0])):
    """"Compose an affine coordinate transformation with a transposition (i.e. flip or rotate in 90° multiples).

    Given a numpy array ``transform`` of an existing transformation
    matrix in homogeneous (3d) coordinates, a transposition mode ``method``,
    as well as a numpy array ``orig`` of the center of the image,
    calculate the affine coordinate transform corresponding to the composition
    of both transformations, which is respectively:

    - ``PIL.Image.FLIP_LEFT_RIGHT``:
      entails translation to the center, followed by pure reflection
      about the y-axis, and subsequent translation back
    - ``PIL.Image.FLIP_TOP_BOTTOM``:
      entails translation to the center, followed by pure reflection
      about the x-axis, and subsequent translation back
    - ``PIL.Image.ROTATE_180``:
      entails translation to the center, followed by pure reflection
      about the origin, and subsequent translation back
    - ``PIL.Image.ROTATE_90``:
      entails translation to the center, followed by pure rotation
      by 90° counter-clockwise, and subsequent translation back
    - ``PIL.Image.ROTATE_270``:
      entails translation to the center, followed by pure rotation
      by 270° counter-clockwise, and subsequent translation back
    - ``PIL.Image.TRANSPOSE``:
      entails translation to the center, followed by pure rotation
      by 90° counter-clockwise and pure reflection about the x-axis,
      and subsequent translation back
    - ``PIL.Image.TRANSVERSE``:
      entails translation to the center, followed by pure rotation
      by 90° counter-clockwise and pure reflection about the y-axis,
      and subsequent translation back

    Return a numpy array of the resulting affine transformation matrix.
    """
    LOG.debug('transposing coordinates with %s around %s', membername(Image, method), str(orig))
    # get rotation matrix for passive rotation/reflection:
    rot90 = np.array([[0, 1, 0],
                      [-1, 0, 0],
                      [0, 0, 1]])
    reflx = np.array([[1, 0, 0],
                      [0, -1, 0],
                      [0, 0, 1]])
    refly = np.array([[-1, 0, 0],
                      [0, 1, 0],
                      [0, 0, 1]])
    transform = shift_coordinates(transform, -orig)
    operations = {
        Image.FLIP_LEFT_RIGHT: [refly],
        Image.FLIP_TOP_BOTTOM: [reflx],
        Image.ROTATE_180: [reflx, refly],
        Image.ROTATE_90: [rot90],
        Image.ROTATE_270: [rot90, reflx, refly],
        Image.TRANSPOSE: [rot90, reflx],
        Image.TRANSVERSE: [rot90, refly]
    }.get(method) # no default
    for operation in operations:
        transform = np.dot(operation, transform)
    transform = shift_coordinates(
        transform,
        # the image (bounding box) may flip with transposition,
        # so we must translate back to the new upper left:
        adjust_canvas_to_transposition(orig, method))
    return transform

def transform_coordinates(polygon, transform=None):
    """Apply an affine transformation to a set of points.
    Augment the 2d numpy array of points ``polygon`` with a an extra
    column of ones (homogeneous coordinates), then multiply with
    the transformation matrix ``transform`` (or the identity matrix),
    and finally remove the extra column from the result.
    """
    if transform is None:
        transform = np.eye(3)
    polygon = np.insert(polygon, 2, 1, axis=1) # make 3d homogeneous coordinates
    polygon = np.dot(transform, polygon.T).T
    # ones = polygon[:,2]
    # assert np.all(np.array_equal(ones, np.clip(ones, 1 - 1e-2, 1 + 1e-2))), \
    #     'affine transform failed' # should never happen
    polygon = np.delete(polygon, 2, axis=1) # remove z coordinate again
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
    return xywh_from_bbox(*bbox_from_points(points))

def parse_json_string_or_file(value='{}'):    # pylint: disable=unused-argument
    """
    Parse a string as either the path to a JSON object or a literal JSON object.

    Empty strings are equivalent to '{}'
    """
    ret = None
    err = None
    if re.fullmatch(r"\s*", value):
        return {}
    try:
        try:
            with open(value, 'r') as f:
                ret = json.load(f)
        except FileNotFoundError:
            ret = json.loads(value.strip())
        except OSError:
            ret = json.loads(value.strip())
        if not isinstance(ret, dict):
            err = ValueError("Not a valid JSON object: '%s' (parsed as '%s')" % (value, ret))
    except json.decoder.JSONDecodeError as e:
        err = ValueError("Error parsing '%s': %s" % (value, e))
    if err:
        raise err       # pylint: disable=raising-bad-type
    return ret
