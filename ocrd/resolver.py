from os import makedirs, getcwd
from os.path import exists, isfile, join, isdir, abspath, dirname
from shutil import copyfile
import tempfile

import requests

from ocrd.constants import TMP_PREFIX
from ocrd.utils import getLogger, safe_filename
from ocrd.workspace import Workspace
from ocrd.model import OcrdMets

log = getLogger('ocrd.resolver')

class Resolver(object):
    """
    Handle Uploads, Downloads, Repository access and manage temporary directories
    """

    def download_to_directory(self, directory, url, basename=None, overwrite=False, subdir=None, src_dir=''):
        """
        Download a file to the workspace.

        Early Shortcut: If url is a file://-URL and that file is already in the directory, keep it there.

        If basename is not given but subdir is, assume user knows what she's doing and use last URL segment as the basename.
        If basename is not given and no subdir is given, use the alnum characters in the URL as the basename.

        Args:
            directory (string): Directory to download files to
            basename (string, None): basename part of the filename on disk.
            url (string): URL to download from
            overwrite (boolean): Whether to overwrite existing files with that name
            subdir (string, None): Subdirectory to create within the directory. Think fileGrp.
            src_dir (string, ''): Directory for resolving relative file names

        Returns:
            Local filename
        """
        log = getLogger('ocrd.resolver.download_to_directory') # pylint: disable=redefined-outer-name
        log.debug("directory=|%s| url=|%s| basename=|%s| overwrite=|%s| subdir=|%s|", directory, url, basename, overwrite, subdir)

        if url is None:
            raise Exception("'url' must be a string")
        if directory is None:
            raise Exception("'directory' must be a string")

        if basename is None:
            if (subdir is not None) or \
                (directory and url.startswith('file://%s' % directory)): # in case downloading a url 'file:///tmp/foo/bar' to directory '/tmp/foo'
                basename = url.rsplit('/', 1)[-1]
            else:
                basename = safe_filename(url)

        if subdir is not None:
            basename = join(subdir, basename)

        outfilename = join(directory, basename)

        if exists(outfilename) and not overwrite:
            log.debug("File already exists and overwrite=False: %s", outfilename)
            return outfilename

        outfiledir = outfilename.rsplit('/', 1)[0]
        #  print(outfiledir)
        if not isdir(outfiledir):
            makedirs(outfiledir)

        log.debug("Downloading <%s> to '%s' (src_dir=%s)", url, outfilename, src_dir)

        # de-scheme file:// URL
        if url.startswith('file://'):
            url = url[len('file://'):]

        # Relativize against src_dir
        if isfile(join(src_dir, url)):
            url = join(src_dir, url)

        # Copy files or download remote assets
        if '://' not in url:
            copyfile(url, outfilename)
        else:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Not found: %s (HTTP %d)" % (url, response.status_code))
            with open(outfilename, 'wb') as outfile:
                outfile.write(response.content)

        return outfilename

    def workspace_from_url(self, mets_url, src_dir=None, dst_dir=None, clobber_mets=False, mets_basename=None, download=False, download_local=False):
        """
        Create a workspace from a METS by URL.

        Sets the mets.xml file

        Arguments:
            mets_url (string): Source mets URL
            src_dir (string, None): Source directory containing the mets.xml
            dst_dir (string, None): Target directory for the workspace
            clobber_mets (boolean, False): Whether to overwrite existing mets.xml. By default existing mets.xml will raise an exception.
            download (boolean, False): Whether to download all the files
            download_local (boolean, False): Whether to download the file://-URL to the new location

        Returns:
            Workspace
        """
        if src_dir and not src_dir.startswith('/'):
            src_dir = abspath(src_dir)
        if dst_dir and not dst_dir.startswith('/'):
            dst_dir = abspath(dst_dir)
        log.debug("workspace_from_url\nmets_url='%s'\nsrc_dir='%s'\ndst_dir='%s'" % (mets_url, src_dir, dst_dir))

        if mets_url is None:
            if src_dir is None:
                raise Exception("Must pass mets_url and/or src_dir to workspace_from_url")
            else:
                mets_url = 'file://%s/%s' % (src_dir, mets_basename)

        # resolve to absolute
        if '://' not in mets_url:
            mets_url = 'file://%s' % abspath(mets_url)

        if dst_dir is None:
            # if mets_url is a file-url assume working directory is source directory
            if mets_url.startswith('file://'):
                # if dst_dir was not given and mets_url is a file assume that
                # dst_dir should be the directory where the mets.xml resides
                dst_dir = dirname(mets_url[len('file://'):])
            else:
                dst_dir = tempfile.mkdtemp(prefix=TMP_PREFIX)
                log.debug("Creating workspace '%s' for METS @ <%s>", dst_dir, mets_url)

        if src_dir is None:
            src_dir = dirname(mets_url[len('file://'):])

        # if mets_basename is not given, use the last URL segment of the mets_url
        if mets_basename is None:
            mets_basename = mets_url \
                .rsplit('/', 1)[-1] \
                .split('?')[0] \
                .split('#')[0]

        dst_mets = join(dst_dir, mets_basename)
        log.debug("Copying mets url '%s' to '%s'", mets_url, dst_mets)
        if 'file://' + dst_mets == mets_url:
            log.debug("Target and source mets are identical")
        else:
            if exists(dst_mets) and not clobber_mets:
                raise Exception("File '%s' already exists but clobber_mets is false" % dst_mets)
            else:
                self.download_to_directory(dst_dir, mets_url, basename=mets_basename)

        workspace = Workspace(self, dst_dir, mets_basename=mets_basename, src_dir=src_dir)

        if download_local or download:
            for file_grp in workspace.mets.file_groups:
                if download_local:
                    for f in workspace.mets.find_files(fileGrp=file_grp, local_only=True):
                        workspace.download_file(f, subdir=file_grp)
                else:
                    workspace.download_files_in_group(file_grp)

        return workspace

    def workspace_from_nothing(self, directory, mets_basename='mets.xml', clobber_mets=False):
        """
        Create an empty workspace.
        """
        if directory is None:
            directory = tempfile.mkdtemp(prefix=TMP_PREFIX)
        if not exists(directory):
            makedirs(directory)

        mets_fpath = join(directory, mets_basename)
        if not clobber_mets and exists(mets_fpath):
            raise Exception("Not clobbering existing mets.xml in '%s'." % directory)
        mets = OcrdMets.empty_mets()
        with open(mets_fpath, 'wb') as fmets:
            log.info("Writing %s", mets_fpath)
            fmets.write(mets.to_xml(xmllint=True))

        return Workspace(self, directory, mets)
