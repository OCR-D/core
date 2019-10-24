import io
from os import makedirs, unlink
from pathlib import Path

import cv2
from PIL import Image
import numpy as np
from atomicwrites import atomic_write
from deprecated.sphinx import deprecated

from ocrd_models import OcrdMets, OcrdExif, OcrdFile
from ocrd_utils import (
    coordinates_of_segment,
    crop_image,
    getLogger,
    image_from_polygon,
    polygon_from_points,
    xywh_from_points,
    pushd_popd,

    MIME_TO_EXT,
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
        baseurl (string) : Base URL to prefix to relative URL.
    """

    def __init__(self, resolver, directory, mets=None, mets_basename='mets.xml', automatic_backup=False, baseurl=None):
        self.resolver = resolver
        self.directory = directory
        self.mets_target = str(Path(directory, mets_basename))
        if mets is None:
            mets = OcrdMets(filename=self.mets_target)
        self.mets = mets
        self.automatic_backup = automatic_backup
        self.baseurl = baseurl
        #  print(mets.to_xml(xmllint=True).decode('utf-8'))
        self.image_cache = {
            'pil': {},
            'cv2': {},
            'exif': {},
        }

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
            # XXX FIXME hacky
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
            # XXX FIXME HACK
            f.local_filename = f.url
            return f

    def remove_file(self, ID, force=False):
        """
        Remove a file from the workspace.

        Arguments:
            ID (string|OcrdFile): ID of the file to delete or the file itself
            force (boolean): Whether to delete from disk as well
        """
        log.debug('Deleting mets:file %s', ID)
        ocrd_file = self.mets.remove_file(ID)
        if force:
            if not ocrd_file:
                raise Exception("File '%s' not found" % ID)
            if not ocrd_file.local_filename:
                raise Exception("File not locally available %s" % ocrd_file)
            with pushd_popd(self.directory):
                log.info("rm %s [cwd=%s]", ocrd_file.local_filename, self.directory)
                unlink(ocrd_file.local_filename)
        return ocrd_file

    def remove_file_group(self, USE, recursive=False, force=False):
        """
        Remove a fileGrp.

        Arguments:
            USE (string): USE attribute of the fileGrp to delete
            recursive (boolean): Whether to recursively delete all files in the group
            force (boolean): When deleting recursively whether to delete files from HDD
        """
        if force and not recursive:
            raise Exception("remove_file_group: force without recursive is likely a logic error")
        if USE not in self.mets.file_groups:
            raise Exception("No such fileGrp: %s" % USE)
        if recursive:
            for f in self.mets.find_files(fileGrp=USE):
                self.remove_file(f.ID, force=force)
        self.mets.remove_file_group(USE)

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

        with pushd_popd(self.directory):
            if 'local_filename' in kwargs:
                local_filename_dir = kwargs['local_filename'].rsplit('/', 1)[0]
                if not Path(local_filename_dir).is_dir():
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

        if image_url not in self.image_cache['exif']:
            # FIXME must be in the right directory
            self.image_cache['exif'][image_url] = OcrdExif(Image.open(image_filename))
        return self.image_cache['exif'][image_url]

    @deprecated(version='1.0.0', reason="Use workspace.image_from_page and workspace.image_from_segment")
    def resolve_image_as_pil(self, image_url, coords=None):
        return self._resolve_image_as_pil(image_url, coords)

    def _resolve_image_as_pil(self, image_url, coords=None):
        """
        Resolve an image URL to a PIL image.

        Args:
            coords (list) : Coordinates of the bounding box to cut from the image

        Returns:
            Image or region in image as PIL.Image
        """
        files = self.mets.find_files(url=image_url)
        f = files[0] if files else OcrdFile(None, url=image_url)
        image_filename = self.download_file(f).local_filename

        if image_url not in self.image_cache['pil']:
            with pushd_popd(self.directory):
                self.image_cache['pil'][image_url] = Image.open(image_filename)

        pil_image = self.image_cache['pil'][image_url]

        if coords is None:
            return pil_image
        if image_url not in self.image_cache['cv2']:
            log.debug("Converting PIL to OpenCV: %s", image_url)
            color_conversion = cv2.COLOR_GRAY2BGR if pil_image.mode in ('1', 'L') else  cv2.COLOR_RGB2BGR
            pil_as_np_array = np.array(pil_image).astype('uint8') if pil_image.mode == '1' else np.array(pil_image)
            self.image_cache['cv2'][image_url] = cv2.cvtColor(pil_as_np_array, color_conversion)
        cv2_image = self.image_cache['cv2'][image_url]
        poly = np.array(coords, np.int32)
        log.debug("Cutting region %s from %s", coords, image_url)
        region_cut = cv2_image[
            np.min(poly[:, 1]):np.max(poly[:, 1]),
            np.min(poly[:, 0]):np.max(poly[:, 0])
        ]
        return Image.fromarray(region_cut)

    def image_from_page(self, page, page_id, feature_selector='', feature_filter=''):
        """Extract a Page image from the workspace.

        Given a PageType object, ``page``, extract its PIL.Image from
        AlternativeImage if it exists. Otherwise extract the PIL.Image
        from imageFilename. Also crop it if a Border exists, and rotate
        it if an @orientation exists. Otherwise just return it.

        If ``feature_selector`` and/or ``feature_filter`` is given, then
        select/filter among imageFilename and all AlternativeImages the
        last which contains all of the selected but none of the filtered
        features (i.e. @comments classes), or raise an error.

        If the chosen image does not have "cropped", but a Border exists,
        then crop it (unless "cropped" is also being filtered). And if the
        chosen image does not have "deskewed", but an @orientation exists,
        then rotate it (unless "deskewed" is also being filtered).

        Cropping uses a polygon mask (not just the rectangle).

        (Required and produced features need not be in the same order, so
        ``feature_selector`` is merely a mask specifying Boolean AND, and
        ``feature_filter`` is merely a mask specifying Boolean OR.)

        If the resulting page image is larger than the bounding box of
        ``page``, then in the returned bounding box, reduce the offset by
        half the width/height difference (so consumers being passed this
        image and offset will still crop relative to the original center).

        Return a tuple:
         * the extracted image,
         * a dictionary with the absolute coordinates of the page's
           bounding box / border (xywh), angle and the AlternativeImage
           @comments (features, i.e. of all operations that lead up to
           this result),
         * an OcrdExif instance associated with the original image.
        (The first two can be used to annotate a new AlternativeImage,
         or pass down with ``image_from_segment``.)

        Example:
         * get a raw (colored) but already deskewed and cropped image:
           ``page_image, page_xywh, page_image_info = workspace.image_from_page(
                 page, page_id,
                 feature_selector='deskewed,cropped',
                 feature_filter='binarized,grayscale_normalized')``
        """
        page_image = self._resolve_image_as_pil(page.imageFilename)
        page_image_info = OcrdExif(page_image)
        page_xywh = {'x': 0,
                     'y': 0,
                     'w': page_image.width,
                     'h': page_image.height}
        # FIXME: remove PrintSpace here as soon as GT abides by the PAGE standard:
        border = page.get_Border() or page.get_PrintSpace()
        if border:
            page_points = border.get_Coords().points
            log.debug("Using explicitly set page border '%s' for page '%s'",
                      page_points, page_id)
            page_xywh = xywh_from_points(page_points)
        # region angle: PAGE orientation is defined clockwise,
        # whereas PIL/ndimage rotation is in mathematical direction:
        page_xywh['angle'] = -(page.get_orientation() or 0)
        # initialize AlternativeImage@comments classes as empty:
        page_xywh['features'] = ''

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
                page_xywh['features'] = features
        # crop, if (still) necessary:
        if (border and
            not 'cropped' in page_xywh['features'] and
            not 'cropped' in feature_filter.split(',')):
            log.debug('Cropping to border')
            # get polygon outline of page border:
            page_polygon = np.array(polygon_from_points(page_points))
            # create a mask from the page polygon:
            page_image = image_from_polygon(page_image, page_polygon)
            # recrop into page rectangle:
            page_image = crop_image(page_image,
                                    box=(page_xywh['x'],
                                         page_xywh['y'],
                                         page_xywh['x'] + page_xywh['w'],
                                         page_xywh['y'] + page_xywh['h']))
            page_xywh['features'] += ',cropped'
        # deskew, if (still) necessary:
        if (page_xywh['angle'] and
            not 'deskewed' in page_xywh['features'] and
            not 'deskewed' in feature_filter.split(',')):
            log.info("Rotating AlternativeImage for page '%s' by %.2f°",
                     page_id, page_xywh['angle'])
            page_image = page_image.rotate(page_xywh['angle'],
                                           expand=True,
                                           #resample=Image.BILINEAR,
                                           fillcolor='white')
            page_xywh['features'] += ',deskewed'
        # verify constraints again:
        if not all(feature in page_xywh['features']
                   for feature in feature_selector.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements ' +
                            'selector="%s" in page "%s"' % (
                                feature_selector, page_id))
        if any(feature in page_xywh['features']
               for feature in feature_filter.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements ' +
                            'filter="%s" in page "%s"' % (
                                feature_filter, page_id))
        # subtract offset from any increase in binary region size over source:
        page_xywh['x'] -= round(0.5 * max(0, page_image.width  - page_xywh['w']))
        page_xywh['y'] -= round(0.5 * max(0, page_image.height - page_xywh['h']))
        return page_image, page_xywh, page_image_info

    def image_from_segment(self, segment, parent_image, parent_xywh, feature_selector='', feature_filter=''):
        """Extract a segment image from its parent's image.

        Given a PIL.Image of the parent, ``parent_image``, with its
        absolute coordinates, ``parent_xywh``, and a PAGE segment
        (TextRegionType / TextLineType / WordType / GlyphType) object
        which is logically contained in it, ``segment``, extract its
        PIL.Image from AlternativeImage if it exists. Otherwise produce
        an image via cropping from ``parent_image``.

        If ``feature_selector`` and/or ``feature_filter`` is given, then
        select/filter among the cropped ``parent_image`` and the available
        AlternativeImages the last which contains all of the selected but none
        of the filtered features (i.e. @comments classes), or raise an error.

        If the chosen AlternativeImage does not have "deskewed", but
        an @orientation exists, then rotate it (unless "deskewed" is
        also being filtered).

        Regardless, respect any orientation angle annotated for the parent
        (from parent-level deskewing) by rotating the image, and compensating
        the segment coordinates in an inverse transformation (i.e. translation
        to center, passive rotation, re-translation).

        Cropping uses a polygon mask (not just the rectangle).

        (Required and produced features need not be in the same order, so
        ``feature_selector`` is merely a mask specifying Boolean AND, and
        ``feature_filter`` is merely a mask specifying Boolean OR.)

        If the resulting segment image is larger than the bounding box of
        ``segment``, then in the returned bounding box, reduce the offset by
        half the width/height difference (so consumers being passed this
        image and offset will still crop relative to the original center).

        Return a tuple:
         * the extracted image,
         * a dictionary with the absolute coordinates of the segment's
           bounding box (xywh), angle and the AlternativeImage @comments
           (features, i.e. of all operations that lead up to this result).
        (These can be used to create a new AlternativeImage, or pass down
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
        # crop:
        segment_xywh = xywh_from_points(segment.get_Coords().points)
        # get polygon outline of segment relative to parent image:
        segment_polygon = coordinates_of_segment(segment, parent_image, parent_xywh)
        # create a mask from the segment polygon:
        segment_image = image_from_polygon(parent_image, segment_polygon)
        # recrop into segment rectangle:
        segment_image = crop_image(segment_image,
                                   box=(segment_xywh['x'] - parent_xywh['x'],
                                        segment_xywh['y'] - parent_xywh['y'],
                                        segment_xywh['x'] - parent_xywh['x'] + segment_xywh['w'],
                                        segment_xywh['y'] - parent_xywh['y'] + segment_xywh['h']))
        if 'orientation' in segment.__dict__:
            # angle: PAGE orientation is defined clockwise,
            # whereas PIL/ndimage rotation is in mathematical direction:
            segment_xywh['angle'] = -(segment.get_orientation() or 0)
        # initialize AlternativeImage@comments classes from parent:
        segment_xywh['features'] = parent_xywh['features'] + ',cropped'

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
                segment_xywh['features'] = features
        # deskew, if (still) necessary:
        if ('angle' in segment_xywh and
            segment_xywh['angle'] and
            not 'deskewed' in segment_xywh['features'] and
            not 'deskewed' in feature_filter.split(',')):
            log.info("Rotating AlternativeImage for segment '%s' by %.2f°",
                     segment.id, segment_xywh['angle'])
            segment_image = segment_image.rotate(segment_xywh['angle'],
                                                 expand=True,
                                                 #resample=Image.BILINEAR,
                                                 fillcolor='white')
            segment_xywh['features'] += ',deskewed'
        # verify constraints again:
        if not all(feature in segment_xywh['features']
                   for feature in feature_selector.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements' +
                            'selector="%s" in segment "%s"' % (
                                feature_selector, segment.id))
        if any(feature in segment_xywh['features']
               for feature in feature_filter.split(',') if feature):
            raise Exception('Found no AlternativeImage that satisfies all requirements ' +
                            'filter="%s" in segment "%s"' % (
                                feature_filter, segment.id))
        # subtract offset from any increase in binary region size over source:
        segment_xywh['x'] -= round(0.5 * max(0,
                                             segment_image.width - segment_xywh['w']))
        segment_xywh['y'] -= round(0.5 * max(0,
                                             segment_image.height - segment_xywh['h']))
        return segment_image, segment_xywh

    # pylint: disable=redefined-builtin
    def save_image_file(self, image,
                        file_id,
                        file_grp,
                        page_id=None,
                        format='PNG',
                        force=True):
        """Store and reference an image as file into the workspace.

        Given a PIL.Image `image`, and an ID `file_id` to use in METS,
        store the image under the fileGrp `file_grp` and physical page
        `page_id` into the workspace (in a file name based on
        the `file_grp`, `file_id` and `format` extension).

        Return the (absolute) path of the created file.
        """
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=format)
        file_path = str(Path(file_grp, '%s.%s' % (file_id, format.lower())))
        out = self.add_file(
            ID=file_id,
            file_grp=file_grp,
            pageId=page_id,
            local_filename=file_path,
            mimetype='image/' + format.lower(),
            content=image_bytes.getvalue(),
            force=force)
        log.info('created file ID: %s, file_grp: %s, path: %s',
                 file_id, file_grp, out.local_filename)
        return file_path
