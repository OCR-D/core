import sys

import numpy as np
from PIL import Image, ImageStat, ImageDraw, ImageChops

from .logging import getLogger
from .introspect import membername

__all__ = [
    'adjust_canvas_to_rotation',
    'adjust_canvas_to_transposition',
    'bbox_from_points',
    'bbox_from_polygon',
    'bbox_from_xywh',
    'coordinates_for_segment',
    'coordinates_of_segment',
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
    'shift_coordinates',
    'transform_coordinates',
    'transpose_coordinates',
    'xywh_from_bbox',
    'xywh_from_points',
    'xywh_from_polygon',
]

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

def polygon_from_points(points):
    """
    Convert polygon coordinates in page representation to polygon coordinates in numeric list representation.
    """
    polygon = []
    for pair in points.split(" "):
        x_y = pair.split(",")
        polygon.append([float(x_y[0]), float(x_y[1])])
    return polygon


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
    LOG = getLogger('ocrd_utils.coords.rotate_coordinates')
    rad = np.deg2rad(angle)
    cos = np.cos(rad)
    sin = np.sin(rad)
    # get rotation matrix for passive rotation:
    rot = np.array([[+cos, sin, 0],
                    [-sin, cos, 0],
                    [0, 0, 1]])
    # shift to center of rotation
    transform = shift_coordinates(transform, -orig)
    # apply pure rotation
    LOG.debug('rotating coordinates by %.2f° around %s', angle, str(orig))
    transform = np.dot(rot, transform)
    # shift back
    transform = shift_coordinates(
        transform,
        #orig)
        # the image (bounding box) increases with rotation,
        # so we must translate back to the new upper left:
        adjust_canvas_to_rotation(orig, angle))
    return transform

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
    LOG = getLogger('ocrd_utils.rotate_image')
    LOG.debug('rotating image by %.2f°', angle)
    if transparency and image.mode in ['RGB', 'L']:
        # ensure no information is lost by adding transparency channel
        # initialized to fully opaque (so cropping and rotation will
        # expose areas as transparent):
        image = image.copy()
        image.putalpha(255)
    if fill == 'background':
        background = ImageStat.Stat(image)
        if len(background.bands) > 1:
            background = background.median
            if image.mode in ['RGBA', 'LA']:
                background[-1] = 0 # fully transparent
            background = tuple(background)
        else:
            background = background.median[0]
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


def shift_coordinates(transform, offset):
    """Compose an affine coordinate transformation with a translation.

    Given a numpy array ``transform`` of an existing transformation
    matrix in homogeneous (3d) coordinates, and a numpy array
    ``offset`` of the translation vector, calculate the affine
    coordinate transform corresponding to the composition of both
    transformations.
    
    Return a numpy array of the resulting affine transformation matrix.
    """
    LOG = getLogger('ocrd_utils.coords.shift_coordinates')
    LOG.debug('shifting coordinates by %s', str(offset))
    shift = np.eye(3)
    shift[0, 2] = offset[0]
    shift[1, 2] = offset[1]
    return np.dot(shift, transform)

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
    LOG = getLogger('ocrd_utils.coords.transpose_coordinates')
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
    LOG = getLogger('ocrd_utils.transpose_image')
    LOG.debug('transposing image with %s', membername(Image, method))
    return image.transpose(method)

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
    LOG = getLogger('ocrd_utils.crop_image')
    if not box:
        box = (0, 0, image.width, image.height)
    elif box[0] < 0 or box[1] < 0 or box[2] > image.width or box[3] > image.height:
        # (It should be invalid in PAGE-XML to extend beyond parents.)
        LOG.warning('crop coordinates (%s) exceed image (%dx%d)',
                    str(box), image.width, image.height)
    LOG.debug('cropping image to %s', str(box))
    xywh = xywh_from_bbox(*box)
    background = ImageStat.Stat(image)
    if len(background.bands) > 1:
        background = tuple(background.median)
    else:
        background = background.median[0]
    new_image = Image.new(image.mode, (xywh['w'], xywh['h']),
                          background) # or 'white'
    new_image.paste(image, (-xywh['x'], -xywh['y']))
    return new_image

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
        background = ImageStat.Stat(image)
        if len(background.bands) > 1:
            background = tuple(background.median)
        else:
            background = background.median[0]
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


def xywh_from_polygon(polygon):
    """Construct a numeric dict representing a bounding box from polygon coordinates in numeric list representation."""
    return xywh_from_bbox(*bbox_from_polygon(polygon))
