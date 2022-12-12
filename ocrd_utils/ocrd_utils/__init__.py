"""
Utility functions and constants usable in various circumstances.

* :py:func:`coordinates_of_segment`,
  :py:func:`coordinates_for_segment`

    These functions convert polygon outlines for PAGE elements on all hierarchy
    levels below page (i.e. region, line, word, glyph) between relative coordinates
    w.r.t. a corresponding image and absolute coordinates w.r.t. the top-level image.
    This includes rotation and offset correction, based on affine transformations.
    (Used by :py:class:`ocrd.workspace.Workspace` methods 
    :py:meth:`ocrd.workspace.Workspace.image_from_page` and 
    :py:meth:`ocrd.workspace.Workspace.image_from_segment`.)

* :py:func:`rotate_coordinates`, 
  :py:func:`shift_coordinates`,
  :py:func:`transpose_coordinates`,
  :py:func:`transform_coordinates`

    These backend functions compose affine transformations for reflection, rotation
    and offset correction of coordinates, or apply them to a set of points. They can be
    used to pass down the coordinate system along with images (both invariably sharing
    the same operations context) when traversing the element hierarchy top to bottom.
    (Used by :py:class:`ocrd.workspace.Workspace` methods
    :py:meth:`ocrd.workspace.Workspace.image_from_page` and 
    :py:meth:`ocrd.workspace.Workspace.image_from_segment`.)

* :py:func:`rotate_image`,
  :py:func:`crop_image`,
  :py:func:`transpose_image`

    These `PIL.Image` functions are safe replacements for the `rotate`, `crop`, and
    `transpose` methods.

* :py:func:`image_from_polygon`,
  :py:func:`polygon_mask`

    These functions apply polygon masks to `PIL.Image` objects.

* :py:func:`xywh_from_points`,
  :py:func:`points_from_xywh`,
  :py:func:`polygon_from_points` etc.

    These functions have the syntax `X_from_Y`, where `X` and `Y` can be:

    * `bbox` is a 4-tuple of integers x0, y0, x1, y1 of the bounding box (rectangle)

      (used by `PIL.Image`)
    * `points` a string encoding a polygon: `"0,0 100,0 100,100, 0,100"`

      (used by PAGE-XML)
    * `polygon` is a list of 2-lists of integers x, y of points forming an (implicitly closed)
      polygon path: `[[0,0], [100,0], [100,100], [0,100]]`

      (used by Open `cv2` and higher-level coordinate functions in :py:mod:`ocrd_utils`)
    * `xywh` a dict with keys for x, y, width and height: `{'x': 0, 'y': 0, 'w': 100, 'h': 100}`

      (produced by `tesserocr` and image/coordinate recursion methods in :py:mod:`ocrd.workspace`)
    * `x0y0x1y1` is a 4-list of strings `x0`, `y0`, `x1`, `y1` of the bounding box (rectangle)

      (produced by `tesserocr`)
    * `y0x0y1x1` is the same as `x0y0x1y1` with positions of `x` and `y` in the list swapped

* :py:func:`is_file_in_directory`
  :py:func:`is_local_filename`,
  :py:func:`safe_filename`,
  :py:func:`abspath`,
  :py:func:`get_local_filename`

    filesystem-related utilities

* :py:func:`is_string`,
  :py:func:`membername`,
  :py:func:`concat_padded`,
  :py:func:`nth_url_segment`,
  :py:func:`remove_non_path_from_url`,
  :py:func:`parse_json_string_with_comments`,
  :py:func:`parse_json_string_or_file`,
  :py:func:`set_json_key_value_overrides`,
  :py:func:`assert_file_grp_cardinality`,
  :py:func:`make_file_id`
  :py:func:`generate_range`

    String and OOP utilities

* :py:data:`MIMETYPE_PAGE`,
  :py:data:`EXT_TO_MIME`,
  :py:data:`MIME_TO_EXT`,
  :py:data:`VERSION`

    Constants

* :py:mod:`logging`,
  :py:func:`setOverrideLogLevel`,
  :py:func:`getLevelName`,
  :py:func:`getLogger`,
  :py:func:`initLogging`

    Exports of :py:mod:`ocrd_utils.logging`

* :py:func:`deprecated_alias`

    Decorator to mark a kwarg as deprecated
"""

from .constants import (
    EXT_TO_MIME,
    MIMETYPE_PAGE,
    MIME_TO_EXT,
    MIME_TO_PIL,
    PIL_TO_MIME,
    REGEX_PREFIX,
    REGEX_FILE_ID,
    RESOURCE_LOCATIONS,
    LOG_FORMAT,
    LOG_TIMEFMT,
    VERSION,
    )

from .deprecate import (
    deprecated_alias)

from .image import (
    adjust_canvas_to_rotation,
    adjust_canvas_to_transposition,
    bbox_from_points,
    bbox_from_polygon,
    bbox_from_xywh,
    coordinates_for_segment,
    coordinates_of_segment,
    crop_image,
    image_from_polygon,
    points_from_bbox,
    points_from_polygon,
    points_from_x0y0x1y1,
    points_from_xywh,
    points_from_y0x0y1x1,
    polygon_from_bbox,
    polygon_from_points,
    polygon_from_x0y0x1y1,
    polygon_from_xywh,
    polygon_mask,
    rotate_coordinates,
    rotate_image,
    shift_coordinates,
    transform_coordinates,
    transpose_coordinates,
    transpose_image,
    xywh_from_bbox,
    xywh_from_points,
    xywh_from_polygon)

from .introspect import (
    set_json_key_value_overrides,
    membername)

from .logging import (
    disableLogging,
    getLevelName,
    getLogger,
    initLogging,
    logging,
    setOverrideLogLevel,
    )

from .os import (
    abspath,
    directory_size,
    get_processor_resource_types,
    get_ocrd_tool_json,
    get_moduledir,
    list_all_resources,
    is_file_in_directory,
    list_resource_candidates,
    atomic_write,
    pushd_popd,
    unzip_file_to_dir,
    )

from .str import (
    assert_file_grp_cardinality,
    concat_padded,
    generate_range,
    get_local_filename,
    is_local_filename,
    is_string,
    make_file_id,
    nth_url_segment,
    parse_json_string_or_file,
    parse_json_string_with_comments,
    remove_non_path_from_url,
    safe_filename)
