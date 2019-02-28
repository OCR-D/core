import os
from os.path import join

import cv2
from PIL import Image
import numpy as np

from ocrd_models import OcrdMets, OcrdExif
from ocrd_utils import getLogger, is_local_filename, abspath

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
        self.mets_target = os.path.join(directory, mets_basename)
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
            url = join(self.baseurl, url)
        return self.resolver.download_to_directory(self.directory, url, **kwargs)

    def download_file(self, f):
        """
        Download a :py:mod:`ocrd.model.ocrd_file.OcrdFile` to the workspace.
        """
        #  os.chdir(self.directory)
        #  log.info('f=%s' % f)
        oldpwd = os.getcwd()
        try:
            os.chdir(self.directory)
            if is_local_filename(f.url):
                f.local_filename = abspath(f.url)
            else:
                if f.local_filename:
                    log.debug("Already downloaded: %s", f.local_filename)
                else:
                    f.local_filename = self.download_url(f.url, basename='%s/%s' % (f.fileGrp, f.ID))
        finally:
            os.chdir(oldpwd)

        #  print(f)
        return f

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

        oldpwd = os.getcwd()
        try:
            os.chdir(self.directory)
            if 'local_filename' in kwargs:
                local_filename_dir = kwargs['local_filename'].rsplit('/', 1)[0]
                if not os.path.isdir(local_filename_dir):
                    os.makedirs(local_filename_dir)
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
            os.chdir(oldpwd)

        return ret

    def save_mets(self):
        """
        Write out the current state of the METS file.
        """
        log.info("Saving mets '%s'" % self.mets_target)
        if self.automatic_backup:
            WorkspaceBackupManager(self).add()
        with open(self.mets_target, 'wb') as f:
            f.write(self.mets.to_xml(xmllint=True))

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

    def resolve_image_as_pil(self, image_url, coords=None):
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
