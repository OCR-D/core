import os

from ocrd.model import OcrdMets, OcrdPage
from ocrd.log import logging as log

class Workspace(object):
    """
    A workspace is a temporary directory set up for a processor. It's the
    interface to the METS/PAGE XML and delegates download and upload to the
    Resolver.
    """

    def __init__(self, resolver, directory):
        self.resolver = resolver
        self.directory = directory
        self.mets = OcrdMets(filename=os.path.join(directory, 'mets.xml'))

    def list_input_files(self):
        """
        List input files, delegates to OcrdMets.
        """
        return self.mets.files_in_group('INPUT')

    def list_output_files(self):
        """
        List output files, delegates to OcrdMets.
        """
        return self.mets.files_in_group('OUTPUT')

    def download_url(self, url, basename=None):
        """
        Download a URL to the workspace.
        """
        return self.resolver.download_to_directory(self.directory, url, basename)

    def download_file(self, mets_file):
        """
        Download a ~OcrdMetsFile to the workspace.
        """
        if mets_file.filename:
            log.debug("Alrady downloaded: %s" % (mets_file.filename))
            filename = mets_file.filename
        else:
            filename = self.download_url(mets_file.url)
            mets_file.filename = filename
        if mets_file.mimetype.startswith('image'):
            return OcrdPage.from_mets_file(mets_file)
        elif mets_file.mimetype == 'text/xml':
            return OcrdPage(filename=filename)

    def download_all_inputs(self):
        """
        Download all  the ~OcrdMetsFile in the INPUT file group.
        """
        for input_file in self.list_input_files():
            self.download_file(input_file)

    def add_output_file(self, basename, ID, mimetype, url):
        """
        Add an output file. Creates the file on-disk in the workspace
        directory, creates an ~OcrdMetsFile to pass around and adds that to the
        OcrdMets OUTPUT section.
        """
        pass

    def persist(self):
        """
        Persist the workspace using the resolver. Uploads the files in the
        OUTPUT group to the data repository, sets their URL accordingly.
        """
        pass
