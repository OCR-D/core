import tempfile
from pathlib import Path

import requests

from ocrd.constants import TMP_PREFIX
from ocrd_utils import (
    getLogger,
    is_local_filename,
    get_local_filename,
    remove_non_path_from_url,
    nth_url_segment
)
from ocrd.workspace import Workspace
from ocrd_models import OcrdMets

log = getLogger('ocrd.resolver')

class Resolver():
    """
    Handle Uploads, Downloads, Repository access and manage temporary directories
    """

    def download_to_directory(self, directory, url, basename=None, overwrite=False, subdir=None):
        """
        Download a file to the workspace.

        Early Shortcut: If url is a local file and that file is already in the directory, keep it there.

        If basename is not given but subdir is, assume user knows what she's doing and use last URL segment as the basename.
        If basename is not given and no subdir is given, use the alnum characters in the URL as the basename.

        Args:
            directory (string): Directory to download files to
            basename (string, None): basename part of the filename on disk.
            url (string): URL to download from
            overwrite (boolean): Whether to overwrite existing files with that name
            subdir (string, None): Subdirectory to create within the directory. Think fileGrp.

        Returns:
            Local filename, __relative__ to directory
        """
        log = getLogger('ocrd.resolver.download_to_directory') # pylint: disable=redefined-outer-name
        log.info("directory=|%s| url=|%s| basename=|%s| overwrite=|%s| subdir=|%s|", directory, url, basename, overwrite, subdir)

        if not url:
            raise Exception("'url' must be a string")
        if not directory:
            raise Exception("'directory' must be a string")  # acutally Path would also work

        directory = Path(directory).resolve(strict=False)
        directory.mkdir(parents=True, exist_ok=True)

        subdir_path = Path(subdir if subdir else '')
        basename_path = Path(basename if basename else nth_url_segment(url))
        ret = str(Path(subdir_path, basename_path))
        dst_path = directory / ret

        #  print('url=%s', url)
        #  print('directory=%s', directory)
        #  print('subdir_path=%s', subdir_path)
        #  print('basename_path=%s', basename_path)
        #  print('ret=%s', ret)
        #  print('dst_path=%s', dst_path)

        src_path = None
        if is_local_filename(url):
            src_path = Path(get_local_filename(url)).resolve(strict=False)
            if not src_path.exists():
                log.error("Failed to resolve URL locally: %s --> %s which doesnt' exist" % (url, src_path))
                raise FileNotFoundError("File path passed as 'url' to download_to_directory does not exist: %s" % url)
            if src_path == dst_path:
                log.debug("Stop early, src_path and dst_path are the same: '%s' (url: '%s')" % (src_path, url))
                return ret

        # Respect 'overwrite' arg
        if dst_path.exists() and not overwrite:
            raise Exception("File already exists and 'overwrite' not set: %s" % (dst_path))

        # Create dst_path parent dir
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy files or download remote assets
        if src_path:
            log.debug("Copying file '%s' to '%s'", src_path, dst_path)
            dst_path.write_bytes(src_path.read_bytes())
        else:
            log.debug("Downloading URL '%s' to '%s'", url, dst_path)
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("HTTP request failed: %s (HTTP %d)" % (url, response.status_code))
            dst_path.write_bytes(response.content)

        return ret

    def workspace_from_url(self, mets_url, dst_dir=None, clobber_mets=False, mets_basename=None, download=False, src_baseurl=None):
        """
        Create a workspace from a METS by URL (i.e. clone it).

        Sets the mets.xml file

        Arguments:
            mets_url (string): Source mets URL
            dst_dir (string, None): Target directory for the workspace
            clobber_mets (boolean, False): Whether to overwrite existing mets.xml. By default existing mets.xml will raise an exception.
            download (boolean, False): Whether to download all the files
            src_baseurl (string, None): Base URL for resolving relative file locations

        Returns:
            Workspace
        """

        if mets_url is None:
            raise Exception("Must pass 'mets_url' workspace_from_url")

        # if mets_basename is not given, use the last URL segment of the mets_url
        if mets_basename is None:
            mets_basename = nth_url_segment(mets_url, -1)

        # If src_baseurl wasn't given, determine from mets_url by removing last url segment
        if not src_baseurl:
            last_segment = nth_url_segment(mets_url)
            src_baseurl = remove_non_path_from_url(remove_non_path_from_url(mets_url)[:-len(last_segment)])

        # resolve dst_dir
        if not dst_dir:
            log.debug("Creating ephemereal workspace '%s' for METS @ <%s>", dst_dir, mets_url)
            dst_dir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        else:
            dst_dir = str(Path(dst_dir).resolve(strict=True))

        log.debug("workspace_from_url\nmets_basename='%s'\nmets_url='%s'\nsrc_baseurl='%s'\ndst_dir='%s'",
            mets_basename, mets_url, src_baseurl, dst_dir)

        self.download_to_directory(dst_dir, mets_url, basename=mets_basename, overwrite=clobber_mets)

        workspace = Workspace(self, dst_dir, mets_basename=mets_basename, baseurl=src_baseurl)

        if download:
            for f in workspace.mets.find_files():
                workspace.download_file(f)

        return workspace

    def workspace_from_nothing(self, directory, mets_basename='mets.xml', clobber_mets=False):
        """
        Create an empty workspace.
        """
        if directory is None:
            directory = tempfile.mkdtemp(prefix=TMP_PREFIX)
        Path(directory).mkdir(parents=True, exist_ok=True)
        mets_path = Path(directory, mets_basename)
        if mets_path.exists() and not clobber_mets:
            raise Exception("METS '%s' already exists in '%s' and clobber_mets not set." % (mets_basename, directory))
        mets = OcrdMets.empty_mets()
        log.info("Writing METS to%s", mets_path)
        mets_path.write_bytes(mets.to_xml(xmllint=True))

        return Workspace(self, directory, mets)
