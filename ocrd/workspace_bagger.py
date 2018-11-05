from os import makedirs
from os.path import join, isdir
from shutil import copyfile
import tempfile
from zipfile import ZipFile

from bagit import Bag

from .constants import BAGIT_TXT, TMP_BAGIT_PREFIX
from .utils import is_local_filename
from .logging import getLogger

tempfile.tempdir = '/tmp' # TODO hard-coded
log = getLogger('ocrd.workspace_bagger')

class WorkspaceBagger(object):
    """
    Serialize/De-serialize from OCRD-ZIP to workspace and back.
    """

    def __init__(self, resolver):
        self.resolver = resolver

    def bag(self,
            workspace,
            ocrd_identifier,
            ocrd_mets='data/mets.xml',
            ocrd_manifestation_depth='full',
           ):
        """
        Bag a workspace

        See https://ocr-d.github.com/ocrd_zip#packing-a-workspace-as-ocrd-zip
        """
        if ocrd_manifestation_depth not in ('full', 'partial'):
            raise Exception("manifestation_depth must be 'full' or 'partial'")

        mets = workspace.mets

        # create bagdir
        bagdir = tempfile.mkdtemp(prefix=TMP_BAGIT_PREFIX)
        log.debug("Created bagdir: %s", bagdir)

        # create bagit.txt
        with open(join(bagdir, 'bagit.txt'), 'wb') as f:
            f.write(BAGIT_TXT.encode('utf-8'))

        # TODO allow filtering by fileGrp@USE and such
        for f in mets.find_files():
            if ocrd_manifestation_depth == 'full' or is_local_filename(f.url):
                file_grp_dir = join(bagdir, 'data', f.fileGrp)
                if not isdir(file_grp_dir):
                    makedirs(file_grp_dir)
                self.resolver.download_to_directory(file_grp_dir, f.url, basename=f.ID)
                f.url = join('data', f.ID)

        # save mets.xml
        with open(join(bagdir, ocrd_mets), 'wb') as f:
            f.write(workspace.mets.to_xml())

        # TODO create bag-info.txt
        bag = Bag(bagdir)

    def spill(self, src):
        """
        Spill a workspace, i.e. unpack it and turn it into a workspace.

        See https://ocr-d.github.com/ocrd_zip#unpacking-ocrd-zip-to-a-workspace
        """
