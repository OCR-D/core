import os
from shutil import copyfile
from zipfile import ZipFile
import tempfile
import requests

from ocrd.constants import TMP_PREFIX, EXT_TO_MIME
from ocrd.utils import getLogger, safe_filename
from ocrd.workspace import Workspace
from ocrd.model import OcrdMets

log = getLogger('ocrd.resolver')
tempfile.tempdir = '/tmp'

class Resolver(object):
    """
    Handle Uploads, Downloads, Repository access and manage temporary directories
    """

    def pack_workspace(self, workspace, zpath=None):
        """
        :TODO:
        Pack a workspace as OCRD-ZIP.

        1. Create a subfolder for every fileGrp@USE
        2. Download all files without local_filename
        3. Create a directory DIR
        3. Copy every mets:file to DIR/mets:fileGrp@USE/mets:file@ID
        4. Replace url of every file with ``file://`` URL relative to DIR
        5. Save mets.xml to DIR
        6. ZIP mets.xml and fileGrp@USE-subfolders and store in workspace.zip

        Args:
            workspace (string) : Workspace to pack as OCRD-ZIP
            zpath (string) : Path to ZIP file to savce

        Returns:
            zip_filename (string) : Path to OCRD-ZIP file
        """
        mets = workspace.mets
        outdir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        log.debug("Temporary directory for packing: %s", outdir)

        if zpath is None:
            zpath = os.path.join(workspace.directory, 'workspace.zip')
        for fileGrp in mets.file_groups:
            fileGrp_dir = os.path.join(outdir, fileGrp)
            # 1.
            if not os.path.isdir(fileGrp_dir):
                log.debug("Create directory %s", fileGrp_dir)
                os.makedirs(fileGrp_dir)
            # 2.
            #  log.error("%s: %s", fileGrp, [str(f) for f in mets.find_files()])
            for f in mets.find_files(fileGrp=fileGrp):
                if f.local_filename is None:
                    #  log.debug("No local file: %s", f)
                    workspace.download_file(f, subdir=fileGrp, basename=f.ID)
                    #  print(f.local_filename)
                # 3.
                new_local_filename = os.path.join(fileGrp_dir, f.ID)
                copyfile(f.local_filename, new_local_filename)
                f.local_filename = new_local_filename
                # 4.
                # TODO PAGE
                f.url = 'file://' + os.path.join(fileGrp, f.ID)
        # 5.
        metspath = os.path.join(outdir, 'mets.xml')
        with open(metspath, 'wb') as fmets:
            fmets.write(mets.to_xml(xmllint=True))
        # 6.
        log.info("Writing to %s", zpath)
        with ZipFile(zpath, 'w') as z:
            z.write(metspath, 'mets.xml')
            for fileGrp in mets.file_groups:
                for f in mets.find_files(fileGrp=fileGrp):
                    z.write(f.local_filename, os.path.join(fileGrp, f.ID))

        return zpath

    def unpack_workspace_from_filename(self, zip_filename, directory=None):
        """

        :TODO:
        Unpack an OCRD-ZIP to a local workspace.

        1. Create directory
        3. Unpack zipfile into it
        4. Initiate workspace

        Args:
            zip_filename (string) : Path to OCRD-ZIP file
        """
        if directory is None:
            directory = tempfile.mkdtemp(prefix=TMP_PREFIX)
        log.debug("Unpacking to %s", directory)
        with ZipFile(zip_filename, 'r') as z:
            z.extractall(path=directory)
        return Workspace(self, directory)

    def download_to_directory(self, directory, url, basename=None, overwrite=False, subdir=None):
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
            subdir (boolean, None): Subdirectory to create within the directory. Think fileGrp.

        Returns:
            Local filename
        """
        log = getLogger('ocrd.resolver.download_to_directory') # pylint: disable=redefined-outer-name
        log.debug("directory=|%s| url=|%s| basename=|%s| overwrite=|%s| subdir=|%s|", directory, url, basename, overwrite, subdir)
        if basename is None:
            if (subdir is not None) or \
                (directory and url.startswith('file://%s' % directory)): # in case downloading a url 'file:///tmp/foo/bar' to directory '/tmp/foo'
                basename = url.rsplit('/', 1)[-1]
            else:
                basename = safe_filename(url)

        if subdir is not None:
            basename = os.path.join(subdir, basename)

        outfilename = os.path.join(directory, basename)

        if os.path.exists(outfilename) and not overwrite:
            log.debug("File already exists and overwrite=False: %s", outfilename)
            return outfilename

        outfiledir = outfilename.rsplit('/', 1)[0]
        #  print(outfiledir)
        if not os.path.isdir(outfiledir):
            os.makedirs(outfiledir)

        log.debug("Downloading <%s> to '%s'", url, outfilename)
        if url.startswith('file://'):
            copyfile(url[len('file://'):], outfilename)
        else:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Not found: %s (HTTP %d)" % (url, response.status_code))
            with open(outfilename, 'wb') as outfile:
                outfile.write(response.content)

        return outfilename

    def workspace_from_url(self, mets_url, directory=None, clobber_mets=False, mets_basename=None, download=False, download_local=False):
        """
        Create a workspace from a METS by URL.

        Sets the mets.xml file
        """
        if directory is not None and not directory.startswith('/'):
            directory = os.path.abspath(directory)

        if mets_url is None:
            if directory is None:
                raise Exception("Must pass mets_url and/or directory to workspace_from_url")
            else:
                mets_url = 'file://%s/%s' % (directory, mets_basename)
        if mets_url.find('://') == -1:
            # resolve to absolute
            mets_url = os.path.abspath(mets_url)
            mets_url = 'file://' + mets_url
        if directory is None:
            # if mets_url is a file-url assume working directory to be  where
            # the mets.xml resides
            if mets_url.startswith('file://'):
                # if directory was not given and mets_url is a file assume that
                # directory should be the directory where the mets.xml resides
                directory = os.path.dirname(mets_url[len('file://'):])
            else:
                directory = tempfile.mkdtemp(prefix=TMP_PREFIX)
                log.debug("Creating workspace '%s' for METS @ <%s>", directory, mets_url)

        # if mets_basename is not given, use the last URL segment of the mets_url
        if mets_basename is None:
            mets_basename = mets_url \
                .rsplit('/', 1)[-1] \
                .split('?')[0] \
                .split('#')[0]

        mets_fpath = os.path.join(directory, mets_basename)
        log.debug("Copying mets url '%s' to '%s'", mets_url, mets_fpath)
        if 'file://' + mets_fpath == mets_url:
            log.debug("Target and source mets are identical")
        else:
            if os.path.exists(mets_fpath) and not clobber_mets:
                raise Exception("File '%s' already exists but clobber_mets is false" % mets_fpath)
            else:
                self.download_to_directory(directory, mets_url, basename=mets_basename)

        workspace = Workspace(self, directory, mets_basename=mets_basename)

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
        if not os.path.exists(directory):
            os.makedirs(directory)

        mets_fpath = os.path.join(directory, mets_basename)
        if not clobber_mets and os.path.exists(mets_fpath):
            raise Exception("Not clobbering existing mets.xml in '%s'." % directory)
        mets = OcrdMets.empty_mets()
        with open(mets_fpath, 'wb') as fmets:
            log.info("Writing %s", mets_fpath)
            fmets.write(mets.to_xml(xmllint=True))

        return Workspace(self, directory, mets)