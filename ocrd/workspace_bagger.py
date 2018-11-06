from datetime import datetime
from os import makedirs, chdir, walk
from os.path import join, isdir, basename, exists, relpath
from shutil import make_archive, rmtree, copyfile
from tempfile import mkdtemp
import re
import tempfile
from zipfile import ZipFile

from bagit import Bag, make_manifests

from .constants import BAGIT_TXT, TMP_BAGIT_PREFIX
from .utils import is_local_filename
from .logging import getLogger
from .workspace import Workspace

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
            dest=None,
            ocrd_mets='mets.xml',
            ocrd_manifestation_depth='full',
            ocrd_base_version_checksum=None,
            no_processes=1,
           ):
        """
        Bag a workspace

        See https://ocr-d.github.com/ocrd_zip#packing-a-workspace-as-ocrd-zip
        """
        if ocrd_manifestation_depth not in ('full', 'partial'):
            raise Exception("manifestation_depth must be 'full' or 'partial'")


        mets = workspace.mets

        # create bagdir
        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)
        chdir(bagdir)

        if dest is None:
            dest = '%s.ocrd.zip' % workspace.directory

        log.info("Bagging %s to %s (temp dir %s)" % (workspace.directory, dest, bagdir))

        # create data dir
        makedirs(join(bagdir, 'data'))

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
                f.url = join(f.fileGrp, f.ID)

        # save mets.xml
        with open(join(bagdir, 'data', ocrd_mets), 'wb') as f:
            f.write(workspace.mets.to_xml())

        # create manifests
        total_bytes, total_files = make_manifests('data', no_processes, algorithms=['SHA512'])

        # create bag-info.txt
        bag = Bag(bagdir)
        bag.info['Ocrd-Identifier'] = ocrd_identifier
        bag.info['Ocrd-Manifestation-Depth'] = ocrd_manifestation_depth
        if ocrd_base_version_checksum:
            bag.info['Ocrd-Base-Version-Checksum'] = ocrd_base_version_checksum
        bag.info['Bagging-Date'] = str(datetime.now())
        bag.info['Payload-Oxum'] = '%s.%s' % (total_bytes, total_files)

        # save bag
        bag.save()

        # ZIP it
        make_archive(dest.replace('.zip', ''), 'zip', bagdir)

        # Remove temporary bagdir
        rmtree(bagdir)

        log.info('Created bag at %s' % dest)
        return dest

    def spill(self, src, dest):
        """
        Spill a workspace, i.e. unpack it and turn it into a workspace.

        See https://ocr-d.github.com/ocrd_zip#unpacking-ocrd-zip-to-a-workspace

        Arguments:
            src (string): Path to OCRD-ZIP
            dest (string): Path to directory to unpack data folder to
        """
        print(dest)

        if exists(dest) and not isdir(dest):
            raise Exception("Not a directory: %s" % dest)

        # If dest is an existing directory, try to derive folder name from src
        if isdir(dest):
            workspace_name = re.sub(r'(\.ocrd)?\.zip$', '', basename(src))
            new_dest = join(dest, workspace_name)
            if exists(new_dest):
                raise Exception("Directory exists: %s" % new_dest)
            dest = new_dest
        if not isdir(dest):
            makedirs(dest)
        print(dest)

        log.info("Spilling %s to %s" % (src, dest))

        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)
        zip_ref = ZipFile(src, 'r')
        zip_ref.extractall(bagdir)
        zip_ref.close()

        datadir = join(bagdir, 'data')
        for root, _, files in walk(datadir):
            for file in files:
                srcfile = join(root, file)
                destdir = join(dest, relpath(root, datadir))
                destfile = join(destdir, file)
                if not exists(destdir):
                    makedirs(destdir)
                log.debug("Copy %s -> %s" % (srcfile, destfile))
                copyfile(srcfile, destfile)

        # TODO validate bagit

        # Drop tempdir
        rmtree(bagdir)

        # Create workspace
        workspace = Workspace(self.resolver, directory=dest)

        # TODO validate workspace

        return workspace

    def validate(self, bag):
        """
        Validate conformance with BagIt and OCR-D bagit profile.

        See:
            - https://ocr-d.github.io/ocrd_zip
            - https://ocr-d.github.io/bagit-profile.json
            - https://ocr-d.github.io/bagit-profile.yml
        """
