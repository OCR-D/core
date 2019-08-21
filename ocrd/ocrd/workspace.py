import io
from os import makedirs, chdir, getcwd, unlink
from os.path import join as pjoin, isdir

import cv2
from PIL import Image
import numpy as np
from atomicwrites import atomic_write
from deprecated.sphinx import deprecated

from ocrd_models import OcrdMets, OcrdExif
from ocrd_utils import (
    abspath,
    coordinates_of_segment,
    crop_image,
    getLogger,
    image_from_polygon,
    is_local_filename,
    polygon_from_points,
    xywh_from_points,
    pushd_popd,
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
        self.mets_target = pjoin(directory, mets_basename)
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
        return 'Workspace[directory=%s, file_groups=%s, files=%s]' % (
            self.directory,
            self.mets.file_groups,
            [str(f) for f in self.mets.find_files()],
        )

    def reload_mets(self):
        """
        Reload METS from disk.
        """
        self.mets = OcrdMets(filename=self.mets_target)

    def download_url(self, url, **kwargs):
        """
        Download a URL to the workspace.

        Args:
            url (string): URL to download to directory
            **kwargs : See :py:mod:`ocrd.resolver.Resolver`

        Returns:
            The local filename of the downloaded file
        """
        if self.baseurl and '://' not in url:
            url = pjoin(self.baseurl, url)
        return self.resolver.download_to_directory(self.directory, url, **kwargs)

    def download_file(self, f):
        """
        Download a :py:mod:`ocrd.model.ocrd_file.OcrdFile` to the workspace.
        """
        #  os.chdir(self.directory)
        #  log.info('f=%s' % f)
        with pushd_popd(self.directory):
            if is_local_filename(f.url):
                f.local_filename = abspath(f.url)
            else:
                if f.local_filename:
                    log.debug("Already downloaded: %s", f.local_filename)
                else:
                    f.local_filename = self.download_url(f.url, basename='%s/%s' % (f.fileGrp, f.ID))

        #  print(f)
        return f

    def remove_file(self, ID, force=False):
        """
        Remove a file from the workspace.

        Arguments:
            ID (string): ID of the file to delete
            force (boolean): Whether to delete from disk as well
        """
        log.debug('Deleting mets:file %s', ID)
        mets_file = self.mets.remove_file(ID)
        if force:
            if not mets_file:
                raise Exception("File '%s' not found" % ID)
            if not mets_file.local_filename:
                raise Exception("File not locally available %s" % mets_file)
            with pushd_popd(self.directory):
                log.info("rm %s [cwd=%s]", mets_file.local_filename, self.directory)
                unlink(mets_file.local_filename)
        return mets_file

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

        oldpwd = getcwd()
        try:
            chdir(self.directory)
            if 'local_filename' in kwargs:
                local_filename_dir = kwargs['local_filename'].rsplit('/', 1)[0]
                if not isdir(local_filename_dir):
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
        finally:
            chdir(oldpwd)

        return ret

    def save_mets(self):
        """
        Write out the current state of the METS file.
        """
        log.info("Saving mets '%s'" % self.mets_target)
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
        if files:
            image_filename = self.download_file(files[0]).local_filename
        else:
            image_filename = self.download_url(image_url)

        if image_url not in self.image_cache['exif']:
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
        if files:
            image_filename = self.download_file(files[0]).local_filename
        else:
            image_filename = self.download_url(image_url)

        if image_url not in self.image_cache['pil']:
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

    def image_from_page(self, page, page_id):
        """Extract the Page image from the workspace.

        Given a PageType object, `page`, extract its PIL.Image from
        AlternativeImage if it exists. Otherwise extract the PIL.Image
        from imageFilename and crop it if a Border exists. Otherwise
        just return it.

        When cropping, respect any orientation angle annotated for
        the page (from page-level deskewing) by rotating the
        cropped image, respectively.

        If the resulting page image is larger than the bounding box of
        `page`, pass down the page's box coordinates with an offset of
        half the width/height difference.

        Return the extracted image, and the absolute coordinates of
        the page's bounding box / border (for passing down), and
        an OcrdExif instance associated with the original image.
        """
        page_image = self._resolve_image_as_pil(page.imageFilename)
        page_image_info = OcrdExif(page_image)
        page_xywh = {'x': 0,
                     'y': 0,
                     'w': page_image.width,
                     'h': page_image.height}
        # region angle: PAGE orientation is defined clockwise,
        # whereas PIL/ndimage rotation is in mathematical direction:
        page_xywh['angle'] = -(page.get_orientation() or 0)
        # FIXME: remove PrintSpace here as soon as GT abides by the PAGE standard:
        border = page.get_Border() or page.get_PrintSpace()
        if border:
            page_points = border.get_Coords().points
            log.debug("Using explictly set page border '%s' for page '%s'",
                      page_points, page_id)
            page_xywh = xywh_from_points(page_points)

        alternative_image = page.get_AlternativeImage()
        if alternative_image:
            # (e.g. from page-level cropping, binarization, deskewing or despeckling)
            # assumes implicit cropping (i.e. page_xywh has been applied already)
            log.debug("Using AlternativeImage %d (%s) for page '%s'",
                      len(alternative_image), alternative_image[-1].get_comments(),
                      page_id)
            page_image = self._resolve_image_as_pil(
                alternative_image[-1].get_filename())
        elif border:
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
            if 'angle' in page_xywh and page_xywh['angle']:
                log.info("About to rotate page '%s' by %.2f°",
                          page_id, page_xywh['angle'])
                page_image = page_image.rotate(page_xywh['angle'],
                                                   expand=True,
                                                   #resample=Image.BILINEAR,
                                                   fillcolor='white')
        # subtract offset from any increase in binary region size over source:
        page_xywh['x'] -= round(0.5 * max(0, page_image.width  - page_xywh['w']))
        page_xywh['y'] -= round(0.5 * max(0, page_image.height - page_xywh['h']))
        return page_image, page_xywh, page_image_info

    def image_from_segment(self, segment, parent_image, parent_xywh):
        """Extract a segment image from its parent's image.

        Given a PIL.Image of the parent, `parent_image`, and
        its absolute coordinates, `parent_xywh`, and a PAGE
        segment (TextRegion / TextLine / Word / Glyph) object
        logically contained in it, `segment`, extract its PIL.Image
        from AlternativeImage (if it exists), or via cropping from
        `parent_image`.

        When cropping, respect any orientation angle annotated for
        the parent (from parent-level deskewing) by compensating the
        segment coordinates in an inverse transformation (translation
        to center, rotation, re-translation).
        Also, mind the difference between annotated and actual size
        of the parent (usually from deskewing), by a respective offset
        into the image. Cropping uses a polygon mask (not just the
        rectangle).

        When cropping, respect any orientation angle annotated for
        the segment (from segment-level deskewing) by rotating the
        cropped image, respectively.

        If the resulting segment image is larger than the bounding box of
        `segment`, pass down the segment's box coordinates with an offset
        of half the width/height difference.

        Return the extracted image, and the absolute coordinates of
        the segment's bounding box (for passing down).
        """
        segment_xywh = xywh_from_points(segment.get_Coords().points)
        if 'orientation' in segment.__dict__:
            # angle: PAGE orientation is defined clockwise,
            # whereas PIL/ndimage rotation is in mathematical direction:
            segment_xywh['angle'] = -(segment.get_orientation() or 0)
        alternative_image = segment.get_AlternativeImage()
        if alternative_image:
            # (e.g. from segment-level cropping, binarization, deskewing or despeckling)
            log.debug("Using AlternativeImage %d (%s) for segment '%s'",
                      len(alternative_image), alternative_image[-1].get_comments(),
                      segment.id)
            segment_image = self._resolve_image_as_pil(
                alternative_image[-1].get_filename())
        else:
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
            if 'angle' in segment_xywh and segment_xywh['angle']:
                log.info("About to rotate segment '%s' by %.2f°",
                          segment.id, segment_xywh['angle'])
                segment_image = segment_image.rotate(segment_xywh['angle'],
                                                     expand=True,
                                                     #resample=Image.BILINEAR,
                                                     fillcolor='white')
        # subtract offset from any increase in binary region size over source:
        segment_xywh['x'] -= round(0.5 * max(0, segment_image.width  - segment_xywh['w']))
        segment_xywh['y'] -= round(0.5 * max(0, segment_image.height - segment_xywh['h']))
        return segment_image, segment_xywh

    # pylint: disable=redefined-builtin
    def save_image_file(self, image,
                        file_id,
                        page_id=None,
                        file_grp='OCR-D-IMG', # or -BIN?
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
        file_path = pjoin(file_grp, file_id + '.' + format.lower())
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
