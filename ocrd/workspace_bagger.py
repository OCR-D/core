from datetime import datetime
from os import makedirs, chdir, walk, getcwd
from os.path import join, isdir, basename, exists, relpath
from shutil import make_archive, rmtree, copyfile, move
from tempfile import mkdtemp
import re
import tempfile
import sys

from pkg_resources import get_distribution
from bagit import Bag, make_manifests

from .constants import BAGIT_TXT, TMP_BAGIT_PREFIX, OCRD_BAGIT_PROFILE_URL, VERSION
from .utils import abspath, is_local_filename, unzip_file_to_dir
from .logging import getLogger
from .workspace import Workspace

tempfile.tempdir = '/tmp' # TODO hard-coded
log = getLogger('ocrd.workspace_bagger')

BACKUPDIR = join('/tmp', TMP_BAGIT_PREFIX + 'backup')

class WorkspaceBagger(object):
    """
    Serialize/De-serialize from OCRD-ZIP to workspace and back.
    """

    def __init__(self, resolver):
        self.resolver = resolver

    def _serialize_bag(self, workspace, bagdir, dest, in_place, skip_zip):
        if in_place:
            if not exists(BACKUPDIR):
                makedirs(BACKUPDIR)
            backupdir = mkdtemp(dir=BACKUPDIR)
            move(workspace.directory, backupdir)
        if skip_zip:
            move(bagdir, dest)
        else:
            make_archive(dest.replace('.zip', ''), 'zip', bagdir)

            # Remove temporary bagdir
            rmtree(bagdir)

    def _bag_mets_files(self, workspace, bagdir, ocrd_manifestation_depth, ocrd_mets, processes):
        mets = workspace.mets

        # TODO allow filtering by fileGrp@USE and such
        oldpwd = getcwd()
        chdir(workspace.directory)
        for f in mets.find_files():
            log.info("Resolving %s", f.url)
            if is_local_filename(f.url):
                f.url = abspath(f.url)
            elif is_local_filename(join(workspace.directory, 'data', f.url)):
                f.url = abspath(join(workspace.directory, 'data', f.url))
            elif ocrd_manifestation_depth != 'full':
                log.info("Not fetching non-local files, skipping %s", f.url)
                continue
            elif not f.url.startswith('http'):
                log.error("Not an http URL: %s", f.url)
                continue
            log.info("Resolved %s", f.url)

            file_grp_dir = join(bagdir, 'data', f.fileGrp)
            if not isdir(file_grp_dir):
                makedirs(file_grp_dir)
            self.resolver.download_to_directory(file_grp_dir, f.url, basename=f.ID)
            f.url = join(f.fileGrp, f.ID)

        # save mets.xml
        with open(join(bagdir, 'data', ocrd_mets), 'wb') as f:
            f.write(workspace.mets.to_xml())

        chdir(bagdir)
        total_bytes, total_files = make_manifests('data', processes, algorithms=['sha512'])
        chdir(oldpwd)
        return total_bytes, total_files

    def _set_bag_info(self, bag, total_bytes, total_files, ocrd_identifier, ocrd_manifestation_depth, ocrd_base_version_checksum):
        bag.info['BagIt-Profile-Identifier'] = OCRD_BAGIT_PROFILE_URL
        bag.info['Bag-Software-Agent'] = 'ocrd/core %s (bagit.py %s, bagit_profile %s) [cmdline: "%s"]' % (
            VERSION, # TODO
            get_distribution('bagit').version,
            get_distribution('bagit_profile').version,
            ' '.join(sys.argv))

        bag.info['Ocrd-Identifier'] = ocrd_identifier
        bag.info['Ocrd-Manifestation-Depth'] = ocrd_manifestation_depth
        if ocrd_base_version_checksum:
            bag.info['Ocrd-Base-Version-Checksum'] = ocrd_base_version_checksum
        bag.info['Bagging-Date'] = str(datetime.now())
        bag.info['Payload-Oxum'] = '%s.%s' % (total_bytes, total_files)

    def bag(self,
            workspace,
            ocrd_identifier,
            dest=None,
            ocrd_mets='mets.xml',
            ocrd_manifestation_depth='full',
            ocrd_base_version_checksum=None,
            processes=1,
            skip_zip=False,
            in_place=False,
            tag_files=None
           ):
        """
        Bag a workspace

        See https://ocr-d.github.com/ocrd_zip#packing-a-workspace-as-ocrd-zip

        Arguments:
            workspace (ocrd.Workspace): workspace to bag
            ord_identifier (string): Ocrd-Identifier in bag-info.txt
            dest (string): Path of the generated OCRD-ZIP.
            ord_mets (string): Ocrd-Mets in bag-info.txt
            ord_manifestation_depth (string): Ocrd-Manifestation-Depth in bag-info.txt
            ord_base_version_checksum (string): Ocrd-Base-Version-Checksum in bag-info.txt
            processes (integer): Number of parallel processes checksumming
            skip_zip (boolean): Whether to leave directory unzipped
            in_place (boolean): Whether to **replace** the workspace with its BagIt variant
            tag_files (list<string>): Path names of additional tag files to be bagged at the root of the bag
        """
        if ocrd_manifestation_depth not in ('full', 'partial'):
            raise Exception("manifestation_depth must be 'full' or 'partial'")
        if in_place and dest is not None:
            raise Exception("Setting 'dest' and 'in_place' is a contradiction")
        if in_place and not skip_zip:
            raise Exception("Unsetting 'skip_zip' and 'in_place' is a contradiction")

        if tag_files is None:
            tag_files = []

        # create bagdir
        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)

        if dest is None:
            if in_place:
                dest = workspace.directory
            elif not skip_zip:
                dest = '%s.ocrd.zip' % workspace.directory
            else:
                dest = '%s.ocrd' % workspace.directory

        log.info("Bagging %s to %s (temp dir %s)", workspace.directory, '(in-place)' if in_place else dest, bagdir)

        # create data dir
        makedirs(join(bagdir, 'data'))

        # create bagit.txt
        with open(join(bagdir, 'bagit.txt'), 'wb') as f:
            f.write(BAGIT_TXT.encode('utf-8'))

        # create manifests
        total_bytes, total_files = self._bag_mets_files(workspace, bagdir, ocrd_manifestation_depth, ocrd_mets, processes)

        # create bag-info.txt
        bag = Bag(bagdir)
        self._set_bag_info(bag, total_bytes, total_files, ocrd_identifier, ocrd_manifestation_depth, ocrd_base_version_checksum)

        for tag_file in tag_files:
            copyfile(tag_file, join(bagdir, basename(tag_file)))

        # save bag
        bag.save()

        # ZIP it
        self._serialize_bag(workspace, bagdir, dest, in_place, skip_zip)

        log.info('Created bag at %s', dest)
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

        # If dest is an existing directory, try to derive its name from src
        if isdir(dest):
            workspace_name = re.sub(r'(\.ocrd)?\.zip$', '', basename(src))
            new_dest = join(dest, workspace_name)
            if exists(new_dest):
                raise Exception("Directory exists: %s" % new_dest)
            dest = new_dest
        if not isdir(dest):
            makedirs(dest)
        print(dest)

        log.info("Spilling %s to %s", src, dest)

        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)
        unzip_file_to_dir(src, bagdir)

        datadir = join(bagdir, 'data')
        for root, _, files in walk(datadir):
            for f in files:
                srcfile = join(root, f)
                destdir = join(dest, relpath(root, datadir))
                destfile = join(destdir, f)
                if not exists(destdir):
                    makedirs(destdir)
                log.debug("Copy %s -> %s", srcfile, destfile)
                copyfile(srcfile, destfile)

        # TODO copy allowed tag files if present

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
