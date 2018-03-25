import os
from shutil import copyfile
import tempfile
import requests

from ocrd.utils import getLogger
from ocrd.resolver_cache import ResolverCache
from ocrd.workspace import Workspace

log = getLogger('ocrd.resolver')
PREFIX = 'pyocrd-'
tempfile.tempdir = '/tmp'

class Resolver(object):
    """
    Handle Uploads, Downloads, Repository access and manage temporary directories
    Optionally cache files.

    Args:
        cache_enabled (Boolean): Whether to cache files. If True, passes kwargs to ~ResolverCache.
        prefer_symlink (Boolean): If True, symlink from cached file to the workspace instead of copying to reduce I/O.
    """

    def __init__(self, cache_enabled=False, prefer_symlink=True, **kwargs):
        """
        """
        self.cache_enabled = cache_enabled
        self.prefer_symlink = prefer_symlink
        self.cache = ResolverCache(**kwargs) if cache_enabled else None

    def _copy_or_symlink(self, src, dst, prefer_symlink=None):
        if prefer_symlink is None:
            prefer_symlink = self.prefer_symlink
        if os.path.exists(dst):
            return
        if prefer_symlink:
            os.symlink(src, dst)
        else:
            copyfile(src, dst)

    def download_to_directory(self, directory, url, basename=None, overwrite=False, subdir=None, prefer_symlink=None):
        """
        Download a file to the workspace.

        Basename defaults to last URL path segment.
        """
        #  print(self, directory, url, basename, overwrite, subdir)
        if basename is None:
            basename = url.rsplit('/', 1)[-1]

        if subdir is not None:
            basename = os.path.join(subdir, basename)

        outfilename = os.path.join(directory, basename)

        if os.path.exists(outfilename) and not overwrite:
            log.info("File already exists and overwrite=False: %s", outfilename)

        outfiledir = outfilename.rsplit('/', 1)[0]
        #  print(outfiledir)
        if not os.path.isdir(outfiledir):
            os.makedirs(outfiledir)

        cached_filename = self.cache.get(url) if self.cache_enabled else False

        if cached_filename:
            log.debug("Found cached version of <%s> at '%s'", url, cached_filename)
            self._copy_or_symlink(cached_filename, outfilename, prefer_symlink)
        else:
            log.debug("Downloading <%s> to '%s'", url, outfilename)
            if url.startswith('file://'):
                self._copy_or_symlink(url[len('file://'):], outfilename, prefer_symlink)
            else:
                with open(outfilename, 'wb') as outfile:
                    response = requests.get(url)
                    if response.status_code != 200:
                        raise Exception("Not found: %s (HTTP %d)" % (url, response.status_code))
                    outfile.write(response.content)

        if self.cache_enabled and not cached_filename:
            cached_filename = self.cache.put(url, filename=outfilename)
            log.debug("Stored in cache <%s> at '%s'", url, cached_filename)

        return outfilename

    def create_workspace(self, mets_url):
        """
        Create a workspace for a processor.

        Sets the mets.xml file
        """
        directory = tempfile.mkdtemp(prefix=PREFIX)
        log.debug("Creating workspace '%s' for METS @ <%s>", directory, mets_url)
        self.download_to_directory(directory, mets_url, basename='mets.xml', prefer_symlink=False)
        return Workspace(self, directory)
