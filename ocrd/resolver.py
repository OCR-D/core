import os
from shutil import copyfile
import tempfile
import requests

from ocrd.workspace import Workspace
from ocrd.log import logging as log

PREFIX = 'pyocrd-'
tempfile.tempdir = '/tmp'

class Resolver(object):
    """
    Handle Uploads, Downloads, Repository access and manage temporary directories
    """

    def download_to_directory(self, directory, url, basename=None, overwrite=False):
        """
        Download a file to the workspace.

        Basename defaults to last URL path segment.
        """
        if basename is None:
            basename = url.rsplit('/', 1)[-1]
        outfilename = os.path.join(directory, basename)
        log.debug("Downloading <%s> to '%s'" % (url, outfilename))
        if (os.path.exists(outfilename) and not overwrite):
            log.info("File already exists and overwrite=False: %s" % outfilename)
        if url.startswith('file://'):
            copyfile(url[len('file://'):], outfilename)
        else:
            with open(outfilename, 'wb') as outfile:
                response = requests.get(url)
                if response.status_code != 200:
                    raise Exception("Not found: %s" % (url))
                outfile.write(response.content)

    def create_workspace(self, mets_url):
        """
        Create a workspace for a processor.

        Sets the mets.xml file
        """
        directory = tempfile.mkdtemp(prefix=PREFIX)
        log.debug("Creating workspace '%s' for METS @ <%s>" % (directory, mets_url))
        self.download_to_directory(directory, mets_url, 'mets.xml')
        return Workspace(self, directory)
