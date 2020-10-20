from datetime import datetime
from os import makedirs
from os.path import join, basename, getsize, abspath
from glob import glob
from shutil import copy
import hashlib

from ocrd_models import OcrdMets
from ocrd_utils import getLogger, atomic_write

from .constants import BACKUP_DIR

def _chksum(s):
    return hashlib.sha256(s).hexdigest()

class WorkspaceBackup():

    @classmethod
    def from_path(cls, d):
        mets_file = join(d, 'mets.xml')
        (chksum, lastmod) = basename(d).split('.', maxsplit=1)
        size = getsize(mets_file)
        mets_xml = OcrdMets(filename=mets_file)
        return cls(chksum, float(lastmod), size, mets_xml)

    def __init__(self, chksum, lastmod, size, mets_xml):
        self.chksum = chksum
        self.lastmod = datetime.fromtimestamp(lastmod)
        self.size = size
        self.mets_xml = mets_xml

    def __str__(self):
        return '%s - %s - %8s B %s' % (
            self.chksum[0:7],
            self.lastmod.strftime('%Y-%m-%d %H:%M:%S'),
            self.size,
            self.mets_xml.file_groups
            )

class WorkspaceBackupManager():
    """
    Manages backups of a workspace in a directory BACKUP_DIR
    """

    def __init__(self, workspace):
        self.workspace = workspace
        self.backup_directory = join(workspace.directory, BACKUP_DIR)

    def restore(self, chksum, choose_first=False):
        """
        Restore mets.xml to previous state
        """
        log = getLogger('ocrd.workspace_backup.restore')
        bak = None
        candidates = glob(join(self.backup_directory, '%s*' % chksum))
        if not candidates:
            log.error("No backup found: %s" % chksum)
            return
        if len(candidates) > 1 and not choose_first:
            raise Exception("Not unique, could be\n%s" % '\n'.join(candidates))
        bak = candidates[0]
        self.add()
        log.info("Restoring from %s/mets.xml" % bak)
        src = join(bak, 'mets.xml')
        dest = self.workspace.mets_target
        log.debug('cp "%s" "%s"', src, dest)
        copy(src, dest)
        self.workspace.reload_mets()

    def add(self):
        """
        Create a backup in <self.backup_directory>
        """
        log = getLogger('ocrd.workspace_backup.add')
        mets_str = self.workspace.mets.to_xml()
        chksum = _chksum(mets_str)
        backups = self.list()
        if backups and backups[0].chksum == chksum:
            log.info('No changes since last backup: %s' % backups[0])
        else:
            timestamp = datetime.now().timestamp()
            d = join(self.backup_directory, '%s.%s' % (chksum, timestamp))
            mets_file = join(d, 'mets.xml')
            log.info("Backing up to %s" % mets_file)
            makedirs(d)
            with atomic_write(mets_file) as f:
                f.write(mets_str.decode('utf-8'))
        return chksum

    def list(self):
        """
        List all backups as WorkspaceBackup objects, sorted descending by lastmod.
        """
        backups = []
        for d in glob(join(self.backup_directory, '*')):
            backups.append(WorkspaceBackup.from_path(d))
        backups.sort(key=lambda b: b.lastmod, reverse=True)
        return backups

    def undo(self):
        """
        Restore to last version
        """
        log = getLogger('ocrd.workspace_backup.undo')
        backups = self.list()
        if backups:
            last_backup = backups[0]
            self.restore(last_backup.chksum, choose_first=True)
        else:
            log.info("No backups, nothing to undo.")
