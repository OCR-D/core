import os
import shutil

import cv2
import PIL
import numpy as np

from ocrd.model import OcrdMets, OcrdExif
from ocrd.utils import getLogger
log = getLogger('ocrd.workspace')

class Workspace(object):
    """
    A workspace is a temporary directory set up for a processor. It's the
    interface to the METS/PAGE XML and delegates download and upload to the
    Resolver.

    Args:

        directory (string) : Foldert to work in
        mets (:class:`OcrdMets`) : OcrdMets representing this workspace. Loaded from 'mets.xml' if ``None``.
    """

    def __init__(self, resolver, directory, mets=None):
        self.resolver = resolver
        self.directory = directory
        self.mets_filename = os.path.join(directory, 'mets.xml')
        if mets is None:
            mets = OcrdMets(filename=self.mets_filename)
        self.mets = mets
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
        self.mets = OcrdMets(filename=self.mets_filename)

    def download_url(self, url, **kwargs):
        """
        Download a URL to the workspace.

        Args:
            url (string): URL to download to directory
            **kwargs : See :py:mod:`ocrd.resolver.Resolver`

        Returns:
            The local filename of the downloaded file
        """
        os.chdir(self.directory)
        return self.resolver.download_to_directory(self.directory, url, **kwargs)

    def download_file(self, f, **kwargs):
        """
        Download a :py:mod:`ocrd.model.ocrd_file.OcrdFile` to the workspace.
        """
        os.chdir(self.directory)
        if f.local_filename:
            log.debug("Alrady downloaded: %s", f.local_filename)
        else:
            f.local_filename = self.download_url(f.url, **kwargs)
        return f

    def download_files_in_group(self, use):
        """
        Download all  the :py:mod:`ocrd.model.ocrd_file.OcrdFile` in the file group given.
        """
        for input_file in self.mets.find_files(fileGrp=use):
            self.download_file(input_file, subdir=use)

    def add_file(self, use, basename=None, content=None, local_filename=None, **kwargs):
        """
        Add an output file. Creates an :class:`OcrdFile` to pass around and adds that to the
        OcrdMets OUTPUT section.
        """
        log.debug('outputfile use=%s basename=%s local_filename=%s content=%s', use, basename, local_filename, content is not None)
        if basename is not None:
            if use is not None:
                basename = os.path.join(use, basename)
            local_filename = os.path.join(self.directory, basename)

        local_filename_dir = local_filename.rsplit('/', 1)[0]
        if not os.path.isdir(local_filename_dir):
            os.makedirs(local_filename_dir)

        if 'url' not in kwargs:
            kwargs['url'] = 'file://' + local_filename

        self.mets.add_file(use, local_filename=local_filename, **kwargs)

        if content is not None:
            with open(local_filename, 'wb') as f:
                f.write(content)

    def move_file(self, fobj, dst):
        """
        Move a fobj within the workspace
        """
        shutil.move(fobj.local_filename, os.path.join(self.directory, dst))

    def persist(self):
        """
        Persist the workspace using the resolver. Uploads the files in the
        OUTPUT group to the data repository, sets their URL accordingly.
        """
        self.save_mets()
        raise Exception("NIH")

    def save_mets(self):
        """
        Write out the current state of the METS file.
        """
        with open(self.mets_filename, 'wb') as f:
            f.write(self.mets.to_xml(xmllint=True))

    def resolve_image_exif(self, image_url):
        """
        Get the EXIF metadata about an image URL as :class:`OcrdExif`

        Args:
            image_url (string) : URL of image

        Return
            :class:`OcrdExif`
        """
        image_filename = self.download_url(image_url)

        if image_url not in self.image_cache['exif']:
            self.image_cache['exif'][image_url] = OcrdExif.from_filename(image_filename)
        return self.image_cache['exif'][image_url]

    def resolve_image_as_pil(self, image_url, coords=None):
        """
        Resolve an image URL to a PIL image.

        Args:
            coords (list) : Coordinates of the bounding box to cut from the image

        Returns:
            Image or region in image as PIL.Image
        """
        image_filename = self.download_url(image_url)

        if image_url not in self.image_cache['pil']:
            self.image_cache['pil'][image_url] = PIL.Image.open(image_filename)

        pil_image = self.image_cache['pil'][image_url]

        if coords is None:
            return pil_image
        else:
            if image_url not in self.image_cache['cv2']:
                self.image_cache['cv2'][image_url] = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            cv2_image = self.image_cache['cv2'][image_url]
            poly = np.array(coords, np.int32)
            region_cut = cv2_image[
                np.min(poly[:, 1]):np.max(poly[:, 1]),
                np.min(poly[:, 0]):np.max(poly[:, 0])
            ]
            return PIL.Image.fromarray(region_cut)
