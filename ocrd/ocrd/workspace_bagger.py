from datetime import datetime
from os import makedirs, chdir, walk
from os.path import join, isdir, basename, exists, relpath
from pathlib import Path
from shutil import make_archive, rmtree, copyfile, move
from tempfile import mkdtemp, TemporaryDirectory
import re
import tempfile
import sys
from bagit import Bag, make_manifests, _load_tag_file, _make_tag_file, _make_tagmanifest_file  # pylint: disable=no-name-in-module
from distutils.dir_util import copy_tree

from ocrd_utils import (
    pushd_popd,
    getLogger,
    is_local_filename,
    unzip_file_to_dir,

    MIMETYPE_PAGE,
    VERSION,
)
from ocrd_validators.constants import BAGIT_TXT, TMP_BAGIT_PREFIX, OCRD_BAGIT_PROFILE_URL
from ocrd_modelfactory import page_from_file
from ocrd_models.ocrd_page import to_xml
from ocrd_utils.package_resources import get_distribution

from .workspace import Workspace

tempfile.tempdir = '/tmp' # TODO hard-coded

BACKUPDIR = join('/tmp', TMP_BAGIT_PREFIX + 'backup')

class WorkspaceBagger():
    """
    Serialize/De-serialize from OCRD-ZIP to workspace and back.
    """

    def __init__(self, resolver, strict=False):
        self.resolver = resolver
        self.strict = strict

    def _serialize_bag(self, workspace, bagdir, dest, skip_zip):
        if skip_zip:
            move(bagdir, dest)
        else:
            make_archive(dest.replace('.zip', ''), 'zip', bagdir)

            # Remove temporary bagdir
            rmtree(bagdir)

    def _log_or_raise(self, msg):
        log = getLogger('ocrd.workspace_bagger')
        if self.strict:
            raise(Exception(msg))
        else:
            log.info(msg)

    def _bag_mets_files(self, workspace, bagdir, ocrd_mets, processes):
        mets = workspace.mets
        changed_urls = {}

        log = getLogger('ocrd.workspace_bagger')
        # TODO allow filtering by fileGrp@USE and such
        with pushd_popd(workspace.directory):
            # URLs of the files before changing
            for f in mets.find_files():
                log.info("Resolving %s", f.url)
                if is_local_filename(f.url):
                    # nothing to do then
                    pass
                elif not f.url.startswith('http'):
                    self._log_or_raise("Not an http URL: %s" % f.url)
                    continue
                log.info("Resolved %s", f.url)

                file_grp_dir = join(bagdir, 'data', f.fileGrp)
                if not isdir(file_grp_dir):
                    makedirs(file_grp_dir)

                _basename = "%s%s" % (f.ID, f.extension)
                _relpath = join(f.fileGrp, _basename)
                self.resolver.download_to_directory(file_grp_dir, f.url, basename=_basename)
                changed_urls[f.url] = _relpath
                f.url = _relpath

            # save mets.xml
            with open(join(bagdir, 'data', ocrd_mets), 'wb') as f:
                f.write(workspace.mets.to_xml())

        # Walk through bagged workspace and fix the PAGE
        # Page/@imageFilename and
        # AlternativeImage/@filename
        bag_workspace = Workspace(self.resolver, directory=join(bagdir, 'data'), mets_basename=ocrd_mets)
        with pushd_popd(bag_workspace.directory):
            for page_file in bag_workspace.mets.find_files(mimetype=MIMETYPE_PAGE):
                pcgts = page_from_file(page_file)
                changed = False
                #  page_doc.set(imageFileName
            #  for old, new in changed_urls:
                for old, new in changed_urls.items():
                    if pcgts.get_Page().imageFilename == old:
                        pcgts.get_Page().imageFilename = new
                        changed = True
                    # TODO replace AlternativeImage, recursively...
                if changed:
                    with open(page_file.url, 'w') as out:
                        out.write(to_xml(pcgts))
                    #  log.info("Replace %s -> %s in %s" % (old, new, page_file))

            chdir(bagdir)
            total_bytes, total_files = make_manifests('data', processes, algorithms=['sha512'])
            log.info("New vs. old: %s" % changed_urls)
        return total_bytes, total_files

    def _set_bag_info(self, bag, total_bytes, total_files, ocrd_identifier, ocrd_base_version_checksum, ocrd_mets='mets.xml'):
        bag.info['BagIt-Profile-Identifier'] = OCRD_BAGIT_PROFILE_URL
        bag.info['Bag-Software-Agent'] = 'ocrd/core %s (bagit.py %s, bagit_profile %s) [cmdline: "%s"]' % (
            VERSION, # TODO
            get_distribution('bagit').version,
            get_distribution('bagit_profile').version,
            ' '.join(sys.argv))

        bag.info['Ocrd-Identifier'] = ocrd_identifier
        if ocrd_base_version_checksum:
            bag.info['Ocrd-Base-Version-Checksum'] = ocrd_base_version_checksum
        bag.info['Bagging-Date'] = str(datetime.now())
        bag.info['Payload-Oxum'] = '%s.%s' % (total_bytes, total_files)
        if ocrd_mets != 'mets.xml':
            bag.info['Ocrd-Mets'] = ocrd_mets

    def bag(self,
            workspace,
            ocrd_identifier,
            dest=None,
            ocrd_mets='mets.xml',
            ocrd_base_version_checksum=None,
            processes=1,
            skip_zip=False,
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
            ord_base_version_checksum (string): Ocrd-Base-Version-Checksum in bag-info.txt
            processes (integer): Number of parallel processes checksumming
            skip_zip (boolean): Whether to leave directory unzipped
            tag_files (list<string>): Path names of additional tag files to be bagged at the root of the bag
        """
        if tag_files is None:
            tag_files = []

        # create bagdir
        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)

        if dest is None:
            if not skip_zip:
                dest = '%s.ocrd.zip' % workspace.directory
            else:
                dest = '%s.ocrd' % workspace.directory

        log = getLogger('ocrd.workspace_bagger')
        log.info("Bagging %s to %s (temp dir %s)", workspace.directory, dest, bagdir)

        # create data dir
        makedirs(join(bagdir, 'data'))

        # create bagit.txt
        with open(join(bagdir, 'bagit.txt'), 'wb') as f:
            f.write(BAGIT_TXT.encode('utf-8'))

        # create manifests
        total_bytes, total_files = self._bag_mets_files(workspace, bagdir, ocrd_mets, processes)

        # create bag-info.txt
        bag = Bag(bagdir)
        self._set_bag_info(bag, total_bytes, total_files, ocrd_identifier, ocrd_base_version_checksum, ocrd_mets=ocrd_mets)

        for tag_file in tag_files:
            copyfile(tag_file, join(bagdir, basename(tag_file)))

        # save bag
        bag.save()

        # ZIP it
        self._serialize_bag(workspace, bagdir, dest, skip_zip)

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
        log = getLogger('ocrd.workspace_bagger')

        if exists(dest) and not isdir(dest):
            raise Exception("Not a directory: %s" % dest)

        # If dest is an existing directory, try to derive its name from src
        if isdir(dest):
            workspace_name = re.sub(r'(\.ocrd)?\.zip$', '', basename(src))
            new_dest = join(dest, workspace_name)
            if exists(new_dest):
                raise Exception("Directory exists: %s" % new_dest)
            dest = new_dest

        log.info("Spilling %s to %s", src, dest)

        bagdir = mkdtemp(prefix=TMP_BAGIT_PREFIX)
        unzip_file_to_dir(src, bagdir)
        bag_info = _load_tag_file(join(bagdir, "bag-info.txt"))

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
        mets_basename = bag_info.get("Ocrd-Mets", "mets.xml")
        workspace = Workspace(self.resolver, directory=dest, mets_basename=mets_basename)

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
        pass

    def recreate_checksums(self, src, dest=None, overwrite=False):
        """
        (Re)creates the files containing the checksums of a bag

        This function uses bag.py to create new files: manifest-sha512.txt and
        tagminifest-sha512.txt for the bag. Also 'Payload-Oxum' in bag-info.txt will be set to the
        appropriate value.

        Arguments:
            src (string):    Path to Bag. May be an zipped or unziped bagit
            dest (string):   Path to where the result should be stored. Not needed if overwrite is
                             set
            overwrite(bool): Replace bag with newly created bag
        """
        if overwrite and dest:
            raise Exception("Setting 'dest' and 'overwrite' is a contradiction")
        if not overwrite and not dest:
            raise Exception("For checksum recreation 'dest' must be provided")
        src_path = Path(src)
        if not src_path.exists():
            raise Exception("Path to bag not existing")
        is_zipped = src_path.is_file()

        with TemporaryDirectory() as tempdir:
            if is_zipped:
                unzip_file_to_dir(src, tempdir)
                path_to_bag = Path(tempdir)
                if not path_to_bag.joinpath("data").exists():
                    raise FileNotFoundError("data directory of bag not found")
            else:
                path_to_bag = src_path if overwrite else Path(dest)
                if not src_path.joinpath("data").exists():
                    raise FileNotFoundError(f"data directory of bag not found at {src}")
                if not overwrite:
                    path_to_bag.mkdir(parents=True, exist_ok=True)
                    copy_tree(src, dest)

            with pushd_popd(path_to_bag):
                n_bytes, n_files = make_manifests("data", 1, ["sha512"])

                bag_infos = _load_tag_file("bag-info.txt")
                bag_infos["Payload-Oxum"] = f"{n_bytes}.{n_files}"
                _make_tag_file("bag-info.txt", bag_infos)
                _make_tagmanifest_file("sha512", ".")

            if is_zipped:
                name = src_path.name
                if name.endswith(".zip"):
                    name = name[:-4]
                zip_path = make_archive(name, "zip", path_to_bag)
                move(zip_path, src if overwrite else dest)
