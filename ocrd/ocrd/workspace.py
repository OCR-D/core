import io
from os import makedirs, unlink, listdir
from pathlib import Path

import cv2
from PIL import Image
import numpy as np
from atomicwrites import atomic_write
from deprecated.sphinx import deprecated

from ocrd_models import OcrdMets, OcrdExif, OcrdFile
from ocrd_models.ocrd_page import parse
from ocrd_utils import (
    getLogger,
    image_from_polygon,
    coordinates_of_segment,
    adjust_canvas_to_rotation,
    adjust_canvas_to_transposition,
    shift_coordinates,
    rotate_coordinates,
    transpose_coordinates,
    crop_image,
    rotate_image,
    transpose_image,
    bbox_from_polygon,
    polygon_from_points,
    xywh_from_bbox,
    pushd_popd,
    MIME_TO_EXT,
    MIME_TO_PIL,
    MIMETYPE_PAGE
)

from .workspace_backup import WorkspaceBackupManager

log = getLogger('ocrd.workspace')


class Workspace():
    """
    A workspace is a temporary directory set up for a processor. It's the
    interface to the METS/PAGE XML and delegates download and upload to the
    Resolver.

    Args:

        directory (string) : Folder to work in
        mets (:class:`OcrdMets`) : OcrdMets representing this workspace. Loaded from 'mets.xml' if ``None``.
        mets_basename (string) : Basename of the METS XML file. Default: Last URL segment of the mets_url.
        overwrite_mode (boolean) : Whether to force add operations on this workspace globally
        baseurl (string) : Base URL to prefix to relative URL.
    """

    def __init__(self, resolver, directory, mets=None, mets_basename='mets.xml', automatic_backup=False, baseurl=None):
        self.resolver = resolver
        self.directory = directory
        self.mets_target = str(Path(directory, mets_basename))
        self.overwrite_mode = False
        if mets is None:
            mets = OcrdMets(filename=self.mets_target)
        self.mets = mets
        self.automatic_backup = automatic_backup
        self.baseurl = baseurl
        #  print(mets.to_xml(xmllint=True).decode('utf-8'))

    def __str__(self):
        return 'Workspace[directory=%s, baseurl=%s, file_groups=%s, files=%s]' % (
            self.directory,
            self.baseurl,
            self.mets.file_groups,
            [str(f) for f in self.mets.find_files()],
        )

    def reload_mets(self):
        """
        Reload METS from disk.
        """
        self.mets = OcrdMets(filename=self.mets_target)


    @deprecated(version='1.0.0', reason="Use workspace.download_file")
    def download_url(self, url, **kwargs):
        """
        Download a URL to the workspace.

        Args:
            url (string): URL to download to directory
            **kwargs : See :py:mod:`ocrd_models.ocrd_file.OcrdFile`

        Returns:
            The local filename of the downloaded file
        """
        f = OcrdFile(None, url=url, **kwargs)
        f = self.download_file(f)
        return f.local_filename


    def download_file(self, f, _recursion_count=0):
        """
        Download a :py:mod:`ocrd.model.ocrd_file.OcrdFile` to the workspace.
        """
        log.debug('download_file %s [_recursion_count=%s]' % (f, _recursion_count))
        with pushd_popd(self.directory):
            try:
                # If the f.url is already a file path, and is within self.directory, do nothing
                url_path = Path(f.url).resolve()
                if not (url_path.exists() and url_path.relative_to(str(Path(self.directory).resolve()))):
                    raise Exception("Not already downloaded, moving on")
            except Exception as e:
                basename = '%s%s' % (f.ID, MIME_TO_EXT.get(f.mimetype, '')) if f.ID else f.basename
                try:
                    f.url = self.resolver.download_to_directory(self.directory, f.url, subdir=f.fileGrp, basename=basename)
                except FileNotFoundError as e:
                    if not self.baseurl:
                        raise Exception("No baseurl defined by workspace. Cannot retrieve '%s'" % f.url)
                    if _recursion_count >= 1:
                        raise Exception("Already tried prepending baseurl '%s'. Cannot retrieve '%s'" % (self.baseurl, f.url))
                    log.debug("First run of resolver.download_to_directory(%s) failed, try prepending baseurl '%s': %s", f.url, self.baseurl, e)
                    f.url = '%s/%s' % (self.baseurl, f.url)
                    f.url = self.download_file(f, _recursion_count + 1).local_filename
            f.local_filename = f.url
            return f

    def remove_file(self, ID, force=False, keep_file=False, page_recursive=False, page_same_group=False):
        """
        Remove a file from the workspace.

        Arguments:
            ID (string|OcrdFile): ID of the file to delete or the file itself
            force (boolean): Continue removing even if file not found in METS
            keep_file (boolean): Whether to keep files on disk
            page_recursive (boolean): Whether to remove all images referenced in the file if the file is a PAGE-XML document.
            page_same_group (boolean): Remove only images in the same file group as the PAGE-XML. Has no effect unless ``page_recursive`` is ``True``.
        """
        log.debug('Deleting mets:file %s', ID)
        if not force and self.overwrite_mode:
            force = True
        if isinstance(ID, OcrdFile):
            ID = ID.ID
        try:
            ocrd_file_ = self.mets.remove_file(ID)
            ocrd_files = [ocrd_file_] if isinstance(ocrd_file_, OcrdFile) else ocrd_file_
            if page_recursive:
                with pushd_popd(self.directory):
                    for ocrd_file in ocrd_files:
                        if ocrd_file.mimetype != MIMETYPE_PAGE:
                            continue
                        ocrd_page = parse(self.download_file(ocrd_file).local_filename, silence=True)
                        for img_url in ocrd_page.get_AllAlternativeImagePaths():
                            img_kwargs = {'url': img_url}
                            if page_same_group:
                                img_kwargs['fileGrp'] = ocrd_file.fileGrp
                            for img_file in self.mets.find_files(**img_kwargs):
                                self.remove_file(img_file, keep_file=keep_file, force=force)
            if not keep_file:
                with pushd_popd(self.directory):
                    for ocrd_file in ocrd_files:
                        if not ocrd_file.local_filename:
                            log.warning("File not locally available %s", ocrd_file)
                            if not force:
                                raise Exception("File not locally available %s" % ocrd_file)
                        else:
                            log.info("rm %s [cwd=%s]", ocrd_file.local_filename, self.directory)
                            unlink(ocrd_file.local_filename)
            return ocrd_file_
        except FileNotFoundError as e:
            if not force:
                raise e

    def remove_file_group(self, USE, recursive=False, force=False, keep_files=False, page_recursive=False, page_same_group=False):
        """
        Remove a fileGrp.

        Arguments:
            USE (string): USE attribute of the fileGrp to delete
            recursive (boolean): Whether to recursively delete all files in the group
            force (boolean): Continue removing even if group or containing files not found in METS
            keep_files (boolean): When deleting recursively whether to keep files on disk
            page_recursive (boolean): Whether to remove all images referenced in the file if the file is a PAGE-XML document.
            page_same_group (boolean): Remove only images in the same file group as the PAGE-XML. Has no effect unless ``page_recursive`` is ``True``.
        """
        if not force and self.overwrite_mode:
            force = True
        if USE not in self.mets.file_groups and not force:
            raise Exception("No such fileGrp: %s" % USE)
        if recursive:
            for f in self.mets.find_files(fileGrp=USE):
                self.remove_file(f, force=force, keep_file=keep_files, page_recursive=page_recursive, page_same_group=page_same_group)
        if USE in self.mets.file_groups:
            self.mets.remove_file_group(USE)
        # XXX this only removes directories in the workspace if they are empty
        # and named after the fileGrp which is a convention in OCR-D.
        with pushd_popd(self.directory):
            if Path(USE).is_dir() and not listdir(USE):
                Path(USE).rmdir()

    def add_file(self, file_grp, content=None, **kwargs):
        """
        Add an output file. Creates an :class:`OcrdFile` to pass around and adds that to the
        OcrdMets OUTPUT section.
        """
        log.debug(
            'outputfile file_grp=%s local_filename=%s content=%s',
            file_grp,
            kwargs.get('local_filename'),
            content is not None)
        if content is not None and 'local_filename' not in kwargs:
            raise Exception("'content' was set but no 'local_filename'")
        if self.overwrite_mode:
            kwargs['force'] = True

        with pushd_popd(self.directory):
            if 'local_filename' in kwargs:
                # If the local filename has folder components, create those folders
                local_filename_dir = kwargs['local_filename'].rsplit('/', 1)[0]
                if local_filename_dir != kwargs['local_filename'] and not Path(local_filename_dir).is_dir():
                    makedirs(local_filename_dir)
                if 'url' not in kwargs:
                    kwargs['url'] = kwargs['local_filename']

            #  print(kwargs)
            ret = self.mets.add_file(file_grp, **kwargs)

            if content is not None:
                with open(kwargs['local_filename'], 'wb') as f:
                    if isinstance(content, str):
                        content = bytes(content, 'utf-8')
                    f.write(content)

        return ret

    def save_mets(self):
        """
        Write out the current state of the METS file.
        """
        log.info("Saving mets '%s'", self.mets_target)
        if self.automatic_backup:
            WorkspaceBackupManager(self).add()
        with atomic_write(self.mets_target, overwrite=True) as f:
            f.write(self.mets.to_xml(xmllint=True).decode('utf-8'))

    def resolve_image_exif(self, image_url):
        """
        Get the EXIF metadata about an image URL as :class:`OcrdExif`

        Args:
            image_url (string) : URL of image

        Return
            :class:`OcrdExif`
        """
        files = self.mets.find_files(url=image_url)
        f = files[0] if files else OcrdFile(None, url=image_url)
        image_filename = self.download_file(f).local_filename
        with Image.open(image_filename) as pil_img:
            ocrd_exif = OcrdExif(pil_img)
        return ocrd_exif

    @deprecated(version='1.0.0', reason="Use workspace.image_from_page and workspace.image_from_segment")
    def resolve_image_as_pil(self, image_url, coords=None):
        return self._resolve_image_as_pil(image_url, coords)

    def _resolve_image_as_pil(self, image_url, coords=None):
        """
        Resolve an image URL to a PIL image.

        Args:
            - coords (list) : Coordinates of the bounding box to cut from the image

        Returns:
            Image or region in image as PIL.Image

        """
        files = self.mets.find_files(url=image_url)
        f = files[0] if files else OcrdFile(None, url=image_url)
        image_filename = self.download_file(f).local_filename

        with pushd_popd(self.directory):
            pil_image = Image.open(image_filename)

        if coords is None:
            return pil_image

        log.debug("Converting PIL to OpenCV: %s", image_url)
        color_conversion = cv2.COLOR_GRAY2BGR if pil_image.mode in ('1', 'L') else  cv2.COLOR_RGB2BGR
        pil_as_np_array = np.array(pil_image).astype('uint8') if pil_image.mode == '1' else np.array(pil_image)
        cv2_image = cv2.cvtColor(pil_as_np_array, color_conversion)

        poly = np.array(coords, np.int32)
        log.debug("Cutting region %s from %s", coords, image_url)
        region_cut = cv2_image[
            np.min(poly[:, 1]):np.max(poly[:, 1]),
            np.min(poly[:, 0]):np.max(poly[:, 0])
        ]
        return Image.fromarray(region_cut)

    def image_from_page(self, page, page_id,
                        fill='background', transparency=False,
                        feature_selector='', feature_filter=''):
        """Extract an image for a PAGE-XML page from the workspace.

        Given ``page``, a PAGE PageType object, extract its PIL.Image,
        either from its AlternativeImage (if it exists), or from its
        @imageFilename (otherwise). Also crop it, if a Border exists,
        and rotate it, if any @orientation angle is annotated.

        If ``feature_selector`` and/or ``feature_filter`` is given, then
        select/filter among the @imageFilename image and the available
        AlternativeImages the last one which contains all of the selected,
        but none of the filtered features (i.e. @comments classes), or
        raise an error.

        (Required and produced features need not be in the same order, so
        ``feature_selector`` is merely a mask specifying Boolean AND, and
        ``feature_filter`` is merely a mask specifying Boolean OR.)

        If the chosen image does not have the feature "cropped" yet, but
        a Border exists, and unless "cropped" is being filtered, then crop it.
        Likewise, if the chosen image does not have the feature "deskewed" yet,
        but an @orientation angle is annotated, and unless "deskewed" is being
        filtered, then rotate it. (However, if @orientation is above the
        [-45°,45°] interval, then apply as much transposition as possible first,
        unless "rotated-90" / "rotated-180" / "rotated-270" is being filtered.)

        Cropping uses a polygon mask (not just the bounding box rectangle).
        Areas outside the polygon will be filled according to ``fill``:

        - if ``background`` (the default),
          then fill with the median color of the image;
        - otherwise, use the given color, e.g. ``white`` or (255,255,255).

        Moreover, if ``transparency`` is true, and unless the image already
        has an alpha channel, then add an alpha channel which is fully opaque
        before cropping and rotating. (Thus, only the exposed areas will be
        transparent afterwards, for those that can interpret alpha channels).

        Return a tuple:

         * the extracted image,
         * a dictionary with information about the extracted image:

           - ``transform``: a Numpy array with an affine transform which
             converts from absolute coordinates to those relative to the image,
             i.e. after cropping to the page's border / bounding box (if any)
             and deskewing with the page's orientation angle (if any)
           - ``angle``: the rotation/reflection angle applied to the image so far,
           - ``features``: the AlternativeImage @comments for the image, i.e.
             names of all operations that lead up to this result,

         * an OcrdExif instance associated with the original image.

        (The first two can be used to annotate a new AlternativeImage,
         or be passed down with ``image_from_segment``.)

        Example:

         * get a raw (colored) but already deskewed and cropped image:

           ``
           page_image, page_coords, page_image_info = workspace.image_from_page(
                 page, page_id,
                 feature_selector='deskewed,cropped',
                 feature_filter='binarized,grayscale_normalized')
           ``
        """
        page_image = self._resolve_image_as_pil(page.imageFilename)
        page_image_info = OcrdExif(page_image)
        border = page.get_Border()
        if (border and
            not 'cropped' in feature_filter.split(',')):
            page_points = border.get_Coords().points
            log.debug("Using explicitly set page border '%s' for page '%s'",
                      page_points, page_id)
            # get polygon outline of page border:
            page_polygon = np.array(polygon_from_points(page_points), dtype=np.int32)
            page_bbox = bbox_from_polygon(page_polygon)
            # subtract offset in affine coordinate transform:
            # (consistent with image cropping or AlternativeImage below)
            page_coords = {
                'transform': shift_coordinates(
                    np.eye(3),
                    np.array([-page_bbox[0],
                              -page_bbox[1]]))
            }
        else:
            page_bbox = [0, 0, page_image.width, page_image.height]
            # use identity as affine coordinate transform:
            page_coords = {
                'transform': np.eye(3)
            }
        # get size of the page after cropping but before rotation:
        page_xywh = xywh_from_bbox(*page_bbox)
        
        # page angle: PAGE @orientation is defined clockwise,
        # whereas PIL/ndimage rotation is in mathematical direction:
        page_coords['angle'] = -(page.get_orientation() or 0)
        # map angle from (-180,180] to [0,360], and partition into multiples of 90;
        # but avoid unnecessary large remainders, i.e. split symmetrically:
        orientation = (page_coords['angle'] + 45) % 360
        orientation = orientation - (orientation % 90)
        skew = (page_coords['angle'] % 360) - orientation
        skew = 180 - (180 - skew) % 360 # map to [-45,45]
        page_coords['angle'] = 0 # nothing applied yet (depends on filters)
        log.debug("page '%s' has orientation=%d skew=%.2f",
                  page_id, orientation, skew)
        
        if (orientation and
            not 'rotated-%d' % orientation in feature_filter.split(',')):
            # Transpose in affine coordinate transform:
            # (consistent with image transposition or AlternativeImage below)
            transposition = { 90: Image.ROTATE_90,
                              180: Image.ROTATE_180,
                              270: Image.ROTATE_270
            }.get(orientation) # no default
            page_coords['transform'] = transpose_coordinates(
                page_coords['transform'],
                transposition,
                np.array([0.5 * page_xywh['w'],
                          0.5 * page_xywh['h']]))
            page_xywh['w'], page_xywh['h'] = adjust_canvas_to_transposition(
                [page_xywh['w'], page_xywh['h']], transposition)
            page_coords['angle'] = orientation
        if (skew and
            not 'deskewed' in feature_filter.split(',')):
            # Rotate around center in affine coordinate transform:
            # (consistent with image rotation or AlternativeImage below)
            page_coords['transform'] = rotate_coordinates(
                page_coords['transform'],
                skew,
                np.array([0.5 * page_xywh['w'],
                          0.5 * page_xywh['h']]))
            page_coords['angle'] += skew
            
        # initialize AlternativeImage@comments classes as empty:
        page_coords['features'] = ''
        
        alternative_image = None
        alternative_images = page.get_AlternativeImage()
        if alternative_images:
            # (e.g. from page-level cropping, binarization, deskewing or despeckling)
            if feature_selector or feature_filter:
                alternative_image = None
                # search from the end, because by convention we always append,
                # and among multiple satisfactory images we want the most recent:
                for alternative_image in reversed(alternative_images):
                    features = alternative_image.get_comments()
                    if (all(feature in features
                            for feature in feature_selector.split(',') if feature) and
                        not any(feature in features
                                for feature in feature_filter.split(',') if feature)):
                        break
                    else:
                        alternative_image = None
            else:
                alternative_image = alternative_images[-1]
                features = alternative_image.get_comments()
            if alternative_image:
                log.debug("Using AlternativeImage %d (%s) for page '%s'",
                          alternative_images.index(alternative_image) + 1,
                          features, page_id)
                page_image = self._resolve_image_as_pil(alternative_image.get_filename())
                page_coords['features'] = features
        
        # crop, if (still) necessary:
        if (border and
            not 'cropped' in page_coords['features'] and
            not 'cropped' in feature_filter.split(',')):
            log.debug("Cropping %s for page '%s' to border", 
                      "AlternativeImage" if alternative_image else "image",
                      page_id)
            # create a mask from the page polygon:
            page_image = image_from_polygon(page_image, page_polygon,
                                            fill=fill, transparency=transparency)
            # recrop into page rectangle:
            page_image = crop_image(page_image, box=page_bbox)
            page_coords['features'] += ',cropped'
        # transpose, if (still) necessary:
        if (orientation and
            not 'rotated-%d' % orientation in page_coords['features'] and
            not 'rotated-%d' % orientation in feature_filter.split(',')):
            log.info("Transposing %s for page '%s' by %d°",
                     "AlternativeImage" if alternative_image else
                     "image", page_id, orientation)
            page_image = transpose_image(page_image, {
                90: Image.ROTATE_90,
                180: Image.ROTATE_180,
                270: Image.ROTATE_270
            }.get(orientation)) # no default
            page_coords['features'] += ',rotated-%d' % orientation
        if (orientation and
            not 'rotated-%d' % orientation in feature_filter.split(',')):
            # FIXME we should enforce consistency here (i.e. split into transposition
            #       and minimal rotation)
            if not (page_image.width == page_xywh['w'] and
                    page_image.height == page_xywh['h']):
                log.error('page "%s" image (%s; %dx%d) has not been transposed properly (%dx%d) during rotation',
                          page_id, page_coords['features'],
                          page_image.width, page_image.height,
                          page_xywh['w'], page_xywh['h'])
        # deskew, if (still) necessary:
        if (skew and
            not 'deskewed' in page_coords['features'] and
            not 'deskewed' in feature_filter.split(',')):
            log.info("Rotating %s for page '%s' by %.2f°",
                     "AlternativeImage" if alternative_image else
                     "image", page_id, skew)
            page_image = rotate_image(page_image, skew,
                                      fill=fill, transparency=transparency)
            page_coords['features'] += ',deskewed'
        if (skew and
            not 'deskewed' in feature_filter.split(',')):
            w_new, h_new = adjust_canvas_to_rotation(
                [page_xywh['w'], page_xywh['h']], skew)
            # FIXME we should enforce consistency here (i.e. rotation always reshapes,
            #       and rescaling never happens)
            if not (w_new - 2 < page_image.width < w_new + 2 and
                    h_new - 2 < page_image.height < h_new + 2):
                log.error('page "%s" image (%s; %dx%d) has not been reshaped properly (%dx%d) during rotation',
                          page_id, page_coords['features'],
                          page_image.width, page_image.height,
                          w_new, h_new)
        
        # verify constraints again:
        if not all(feature in page_coords['features']
                   for feature in feature_selector.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements ' +
                            'selector="%s" in page "%s"' % (
                                feature_selector, page_id))
        if any(feature in page_coords['features']
               for feature in feature_filter.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements ' +
                            'filter="%s" in page "%s"' % (
                                feature_filter, page_id))
        page_image.format = 'PNG' # workaround for tesserocr#194
        return page_image, page_coords, page_image_info

    def image_from_segment(self, segment, parent_image, parent_coords,
                           fill='background', transparency=False,
                           feature_selector='', feature_filter=''):
        """Extract an image for a PAGE-XML hierarchy segment from its parent's image.

        Given...

         * ``parent_image``, a PIL.Image of the parent, with
         * ``parent_coords``, a dict with information about ``parent_image``:
           - ``transform``: a Numpy array with an affine transform which
             converts from absolute coordinates to those relative to the image,
             i.e. after applying all operations (starting with the original image)
           - ``angle``: the rotation/reflection angle applied to the image so far,
           - ``features``: the AlternativeImage @comments for the image, i.e.
             names of all operations that lead up to this result, and
         * ``segment``, a PAGE segment object logically contained in it
           (i.e. TextRegionType / TextLineType / WordType / GlyphType),

        ...extract the segment's corresponding PIL.Image, either from
        AlternativeImage (if it exists), or producing a new image via
        cropping from ``parent_image`` (otherwise).

        If ``feature_selector`` and/or ``feature_filter`` is given, then
        select/filter among the cropped ``parent_image`` and the available
        AlternativeImages the last one which contains all of the selected,
        but none of the filtered features (i.e. @comments classes), or
        raise an error.

        (Required and produced features need not be in the same order, so
        ``feature_selector`` is merely a mask specifying Boolean AND, and
        ``feature_filter`` is merely a mask specifying Boolean OR.)

        Cropping uses a polygon mask (not just the bounding box rectangle).
        Areas outside the polygon will be filled according to ``fill``:

        - if ``background`` (the default),
          then fill with the median color of the image;
        - otherwise, use the given color, e.g. ``white`` or (255,255,255).

        Moreover, if ``transparency`` is true, and unless the image already
        has an alpha channel, then add an alpha channel which is fully opaque
        before cropping and rotating. (Thus, only the exposed areas will be
        transparent afterwards, for those that can interpret alpha channels).

        When cropping, compensate any @orientation angle annotated for the
        parent (from parent-level deskewing) by rotating the segment coordinates
        in an inverse transformation (i.e. translation to center, then passive
        rotation, and translation back).

        Regardless, if any @orientation angle is annotated for the segment
        (from segment-level deskewing), and the chosen image does not have
        the feature "deskewed" yet, and unless "deskewed" is being filtered,
        then rotate it - compensating for any previous ``angle``. (However,
        if @orientation is above the [-45°,45°] interval, then apply as much
        transposition as possible first, unless "rotated-90" / "rotated-180" /
        "rotated-270" is being filtered.)

        Return a tuple:

         * the extracted image,
         * a dictionary with information about the extracted image:
           - ``transform``: a Numpy array with an affine transform which
             converts from absolute coordinates to those relative to the image,
             i.e. after applying all parent operations, and then cropping to
             the segment's bounding box, and deskewing with the segment's
             orientation angle (if any)
           - ``angle``: the rotation/reflection angle applied to the image so far,
           - ``features``: the AlternativeImage @comments for the image, i.e.
             names of all operations that lead up to this result.

        (These can be used to create a new AlternativeImage, or passed down
         for calls on lower hierarchy levels.)

        Example:

         * get a raw (colored) but already deskewed and cropped image:

           ``image, xywh = workspace.image_from_segment(region,
                 page_image, page_xywh,
                 feature_selector='deskewed,cropped',
                 feature_filter='binarized,grayscale_normalized')``
        """
        # note: We should mask overlapping neighbouring segments here,
        # but finding the right clipping rules can be difficult if operating
        # on the raw (non-binary) image data alone: for each intersection, it
        # must be decided which one of either segment or neighbour to assign,
        # e.g. an ImageRegion which properly contains our TextRegion should be
        # completely ignored, but an ImageRegion which is properly contained
        # in our TextRegion should be completely masked, while partial overlap
        # may be more difficult to decide. On the other hand, on the binary image,
        # we can use connected component analysis to mask foreground areas which
        # originate in the neighbouring regions. But that would introduce either
        # the assumption that the input has already been binarized, or a dependency
        # on some ad-hoc binarization method. Thus, it is preferable to use
        # a dedicated processor for this (which produces clipped AlternativeImage
        # or reduced polygon coordinates).
        
        # get polygon outline of segment relative to parent image:
        segment_polygon = coordinates_of_segment(segment, parent_image, parent_coords)
        # get relative bounding box:
        segment_bbox = bbox_from_polygon(segment_polygon)
        # get size of the segment in the parent image after cropping
        # (i.e. possibly different from size before rotation at the parent, but
        #  also possibly different from size after rotation below/AlternativeImage):
        segment_xywh = xywh_from_bbox(*segment_bbox)
        # create a mask from the segment polygon:
        segment_image = image_from_polygon(parent_image, segment_polygon,
                                           fill=fill, transparency=transparency)
        # recrop into segment rectangle:
        segment_image = crop_image(segment_image, box=segment_bbox)
        # subtract offset from parent in affine coordinate transform:
        # (consistent with image cropping)
        segment_coords = {
            'transform': shift_coordinates(
                parent_coords['transform'],
                np.array([-segment_bbox[0],
                          -segment_bbox[1]]))
        }
        
        if 'orientation' in segment.__dict__:
            # region angle: PAGE @orientation is defined clockwise,
            # whereas PIL/ndimage rotation is in mathematical direction:
            segment_coords['angle'] = -(segment.get_orientation() or 0)
        else:
            segment_coords['angle'] = 0
        if segment_coords['angle']:
            # @orientation is always absolute; if higher levels
            # have already rotated, then we must compensate:
            angle = segment_coords['angle'] - parent_coords['angle']
            # map angle from (-180,180] to [0,360], and partition into multiples of 90;
            # but avoid unnecessary large remainders, i.e. split symmetrically:
            orientation = (angle + 45) % 360
            orientation = orientation - (orientation % 90)
            skew = (angle % 360) - orientation
            skew = 180 - (180 - skew) % 360 # map to [-45,45]
            log.debug("segment '%s' has orientation=%d skew=%.2f",
                      segment.id, orientation, skew)
        else:
            orientation = 0
            skew = 0
        segment_coords['angle'] = parent_coords['angle'] # nothing applied yet (depends on filters)

        if (orientation and
            not 'rotated-%d' % orientation in feature_filter.split(',')):
            # Transpose in affine coordinate transform:
            # (consistent with image transposition or AlternativeImage below)
            transposition = { 90: Image.ROTATE_90,
                              180: Image.ROTATE_180,
                              270: Image.ROTATE_270
            }.get(orientation) # no default
            segment_coords['transform'] = transpose_coordinates(
                segment_coords['transform'],
                transposition,
                np.array([0.5 * segment_xywh['w'],
                          0.5 * segment_xywh['h']]))
            segment_xywh['w'], segment_xywh['h'] = adjust_canvas_to_transposition(
                [segment_xywh['w'], segment_xywh['h']], transposition)
            segment_coords['angle'] += orientation
        if (skew and
            not 'deskewed' in feature_filter.split(',')):
            # Rotate around center in affine coordinate transform:
            # (consistent with image rotation or AlternativeImage below)
            segment_coords['transform'] = rotate_coordinates(
                segment_coords['transform'],
                skew,
                np.array([0.5 * segment_xywh['w'],
                          0.5 * segment_xywh['h']]))
            segment_coords['angle'] += skew
            
        # initialize AlternativeImage@comments classes from parent, except
        # for those operations that can apply on multiple hierarchy levels:
        segment_coords['features'] = ','.join(
            [feature for feature in parent_coords['features'].split(',')
             if feature in ['binarized', 'grayscale_normalized',
                            'despeckled', 'dewarped']])
        
        alternative_image = None
        alternative_images = segment.get_AlternativeImage()
        if alternative_images:
            # (e.g. from segment-level cropping, binarization, deskewing or despeckling)
            if feature_selector or feature_filter:
                alternative_image = None
                # search from the end, because by convention we always append,
                # and among multiple satisfactory images we want the most recent:
                for alternative_image in reversed(alternative_images):
                    features = alternative_image.get_comments()
                    if (all(feature in features
                            for feature in feature_selector.split(',') if feature) and
                        not any(feature in features
                                for feature in feature_filter.split(',') if feature)):
                        break
                    else:
                        alternative_image = None
            else:
                alternative_image = alternative_images[-1]
                features = alternative_image.get_comments()
            if alternative_image:
                log.debug("Using AlternativeImage %d (%s) for segment '%s'",
                          alternative_images.index(alternative_image) + 1,
                          features, segment.id)
                segment_image = self._resolve_image_as_pil(alternative_image.get_filename())
                segment_coords['features'] = features
        # transpose, if (still) necessary:
        if (orientation and
            not 'rotated-%d' % orientation in segment_coords['features'] and
            not 'rotated-%d' % orientation in feature_filter.split(',')):
            log.info("Transposing %s for segment '%s' by %d°",
                     "AlternativeImage" if alternative_image else
                     "image", segment.id, orientation)
            segment_image = transpose_image(segment_image, {
                90: Image.ROTATE_90,
                180: Image.ROTATE_180,
                270: Image.ROTATE_270
            }.get(orientation)) # no default
            segment_coords['features'] += ',rotated-%d' % orientation
        if (orientation and
            not 'rotated-%d' % orientation in feature_filter.split(',')):
            # FIXME we should enforce consistency here (i.e. split into transposition
            #       and minimal rotation)
            if not (segment_image.width == segment_xywh['w'] and
                    segment_image.height == segment_xywh['h']):
                log.error('segment "%s" image (%s; %dx%d) has not been transposed properly (%dx%d) during rotation',
                          segment.id, segment_coords['features'],
                          segment_image.width, segment_image.height,
                          segment_xywh['w'], segment_xywh['h'])
        # deskew, if (still) necessary:
        if (skew and
            not 'deskewed' in segment_coords['features'] and
            not 'deskewed' in feature_filter.split(',')):
            log.info("Rotating %s for segment '%s' by %.2f°",
                     "AlternativeImage" if alternative_image else
                     "image", segment.id, skew)
            segment_image = rotate_image(segment_image, skew,
                                         fill=fill, transparency=transparency)
            segment_coords['features'] += ',deskewed'
        if (skew and
            not 'deskewed' in feature_filter.split(',')):
            # FIXME we should enforce consistency here (i.e. rotation always reshapes,
            #       and rescaling never happens)
            w_new, h_new = adjust_canvas_to_rotation(
                [segment_xywh['w'], segment_xywh['h']], skew)
            if not (w_new - 2 < segment_image.width < w_new + 2 and
                    h_new - 2 < segment_image.height < h_new + 2):
                log.error('segment "%s" image (%s; %dx%d) has not been reshaped properly (%dx%d) during rotation',
                          segment.id, segment_coords['features'],
                          segment_image.width, segment_image.height,
                          w_new, h_new)
        else:
            # FIXME: currently unavoidable with line-level dewarping (which increases height)
            if not (segment_xywh['w'] - 2 < segment_image.width < segment_xywh['w'] + 2 and
                    segment_xywh['h'] - 2 < segment_image.height < segment_xywh['h'] + 2):
                log.error('segment "%s" image (%s; %dx%d) has not been cropped properly (%dx%d)',
                          segment.id, segment_coords['features'],
                          segment_image.width, segment_image.height,
                          segment_xywh['w'], segment_xywh['h'])
            
        # verify constraints again:
        if not all(feature in segment_coords['features']
                   for feature in feature_selector.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements' +
                            'selector="%s" in segment "%s"' % (
                                feature_selector, segment.id))
        if any(feature in segment_coords['features']
               for feature in feature_filter.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements ' +
                            'filter="%s" in segment "%s"' % (
                                feature_filter, segment.id))
        segment_image.format = 'PNG' # workaround for tesserocr#194
        return segment_image, segment_coords

    # pylint: disable=redefined-builtin
    def save_image_file(self, image,
                        file_id,
                        file_grp,
                        page_id=None,
                        mimetype='image/png',
                        force=False):
        """Store and reference an image as file into the workspace.

        Given a PIL.Image `image`, and an ID `file_id` to use in METS,
        store the image under the fileGrp `file_grp` and physical page
        `page_id` into the workspace (in a file name based on
        the `file_grp`, `file_id` and `format` extension).

        Return the (absolute) path of the created file.
        """
        if not force and self.overwrite_mode:
            force = True
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=MIME_TO_PIL[mimetype])
        file_path = str(Path(file_grp, '%s%s' % (file_id, MIME_TO_EXT[mimetype])))
        out = self.add_file(
            ID=file_id,
            file_grp=file_grp,
            pageId=page_id,
            local_filename=file_path,
            mimetype=mimetype,
            content=image_bytes.getvalue(),
            force=force)
        log.info('created file ID: %s, file_grp: %s, path: %s',
                 file_id, file_grp, out.local_filename)
        return file_path
