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
        log.debug("directory=|%s| url=|%s| basename=|%s| overwrite=|%s| subdir=|%s|", directory, url, basename, overwrite, subdir)

        if not url:
            raise Exception("'url' must be a string")
        if not directory:
            raise Exception("'directory' must be a string")  # acutally Path would also work

        directory = Path(directory).resolve(strict=False)
        directory.mkdir(parents=True, exist_ok=True)

        subdir_path = Path(subdir if subdir else '')
        basename_path = Path(basename if basename else nth_url_segment(url))
        dst_rel_path = subdir_path / basename_path
        dst_path = directory / dst_rel_path

        print('url=%s', url)
        print('directory=%s', directory)
        print('subdir_path=%s', subdir_path)
        print('basename_path=%s', basename_path)
        print('dst_rel_path=%s', dst_rel_path)
        print('dst_path=%s', dst_path)

        src_path = None
        if is_local_filename(url):
            src_path = Path(get_local_filename(url)).resolve(strict=False)
            if not src_path.exists():
                log.error("File path passed as 'url' to download_to_directory does not exist: %s" % url)
                raise FileNotFoundError("File path passed as 'url' to download_to_directory does not exist: %s" % url)
            try:
                if src_path.relative_to(directory) == dst_rel_path:
                    log.debug("Stop early, src url '%s' already in dst dir %s as '%s'" % (url, directory, dst_rel_path))
                    return str(dst_rel_path)
            except ValueError as e:
                log.debug(e)

        # Respect 'overwrite' arg
        if dst_path.exists() and not overwrite:
            raise Exception("File already exists and overwrite=False: %s" % dst_path)

        # Create dst_path parent dir
        #  dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy files or download remote assets
        if src_path:
            log.debug("Copying file '%s' to '%s'")
            dst_path.write_bytes(src_path.read_bytes())
        else:
            log.debug("Downloading URL '%s' to '%s'", url, dst_path)
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("HTTP request failed: %s (HTTP %d)" % (url, response.status_code))
            dst_path.write_bytes(response.content)

        return str(dst_rel_path)

    def workspace_from_url(self, mets_url, dst_dir=None, clobber_mets=False, mets_basename=None, download=False, baseurl=None):
        """
        Create a workspace from a METS by URL (i.e. clone it).

        Sets the mets.xml file

        Arguments:
            mets_url (string): Source mets URL
            dst_dir (string, None): Target directory for the workspace
            clobber_mets (boolean, False): Whether to overwrite existing mets.xml. By default existing mets.xml will raise an exception.
            download (boolean, False): Whether to download all the files
            baseurl (string, None): Base URL for resolving relative file locations

        Returns:
            Workspace
        """

        if mets_url is None:
            if baseurl is None:
                raise Exception("Must pass mets_url and/or baseurl to workspace_from_url")
            mets_url = '%s/%s' % (baseurl, mets_basename if mets_basename else 'mets.xml')

        # if mets_basename is not given, use the last URL segment of the mets_url
        if mets_basename is None:
            mets_basename = nth_url_segment(mets_url, -1)

        # Resolve baseurl
        if is_local_filename(mets_url):
            mets_path = Path(get_local_filename(mets_url)).resolve(strict=True)
            mets_url = str(mets_path)
            if not baseurl:
                baseurl = str(mets_path.parent)
        # If baseurl wasn't given, determine from mets_url by removing last url
        elif not baseurl:
            last_segment = nth_url_segment(mets_url)
            baseurl = remove_non_path_from_url(remove_non_path_from_url(mets_url)[:-len(last_segment)])

        # Resolve baseurl
        if is_local_filename(baseurl):
            baseurl = str(Path(get_local_filename(baseurl)).resolve(strict=True))

        # resolve dst_dir
        if not dst_dir:
            # if mets_url is a local file assume working directory is source directory
            if is_local_filename(mets_url):
                # if dst_dir was not given and mets_url is a file assume that
                # dst_dir should be the directory where the mets.xml resides
                dst_dir = baseurl
            else:
                dst_dir = tempfile.mkdtemp(prefix=TMP_PREFIX)
                log.debug("Creating ephemereal workspace '%s' for METS @ <%s>", dst_dir, mets_url)
        dst_dir = str(Path(dst_dir).resolve(strict=False))

        log.debug("workspace_from_url\nmets_basename='%s'\nmets_url='%s'\nbaseurl='%s'\ndst_dir='%s'", mets_basename, mets_url, baseurl, dst_dir)

        if dst_dir != baseurl:
            dst_mets = Path(dst_dir, mets_basename)
            log.debug("Copying mets url '%s' to '%s'", mets_url, dst_mets)
            if dst_mets.exists() and not clobber_mets:
                raise Exception("METS '%s' already exists in '%s' and clobber_mets not set" % (mets_basename, dst_dir))
            self.download_to_directory(dst_dir, mets_url, basename=mets_basename)

        workspace = Workspace(self, dst_dir, mets_basename=mets_basename, baseurl=baseurl)

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
