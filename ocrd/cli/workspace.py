import os
import sys
from tempfile import mkdtemp

import click

from ocrd import Resolver, Workspace, WorkspaceValidator, WorkspaceBackupManager
from ocrd.utils import getLogger
from ocrd.constants import TMP_PREFIX

log = getLogger('ocrd.cli.workspace')

class WorkspaceCtx(object):

    def __init__(self, directory, mets_basename, automatic_backup):
        self.directory = directory
        self.resolver = Resolver()
        self.mets_basename = mets_basename
        self.automatic_backup = automatic_backup

pass_workspace = click.make_pass_decorator(WorkspaceCtx)

# ----------------------------------------------------------------------
# ocrd workspace
# ----------------------------------------------------------------------

@click.group("workspace")
@click.option('-d', '--directory', envvar='WORKSPACE_DIR', default='.', type=click.Path(file_okay=False), metavar='WORKSPACE_DIR', help='Changes the workspace folder location.', show_default=True)
@click.option('-M', '--mets-basename', default="mets.xml", help='The basename of the METS file.', show_default=True)
@click.option('--backup', default=False, help="Backup mets.xml whenever it is saved.", is_flag=True)
@click.pass_context
def workspace_cli(ctx, directory, mets_basename, backup):
    """
    Working with workspace
    """
    ctx.obj = WorkspaceCtx(os.path.abspath(directory), mets_basename, automatic_backup=backup)

# ----------------------------------------------------------------------
# ocrd workspace validate
# ----------------------------------------------------------------------

@workspace_cli.command('validate', help='''

    Validate a workspace

''')
@pass_workspace
@click.option('-a', '--download', is_flag=True, help="Download all files")
@click.option('-s', '--skip', help="Tests to skip", default=[], multiple=True, type=click.Choice(['mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density']))
@click.argument('mets_url')
def validate_workspace(ctx, mets_url, download, skip):
    report = WorkspaceValidator.validate_url(ctx.resolver, mets_url, src_dir=ctx.directory, skip=skip, download=download)
    print(report.to_xml())
    if not report.is_valid:
        sys.exit(128)

# ----------------------------------------------------------------------
# ocrd workspace clone
# ----------------------------------------------------------------------

@workspace_cli.command('clone')
@click.option('-f', '--clobber-mets', help="Overwrite existing METS file", default=False, is_flag=True)
@click.option('-a', '--download', is_flag=True, help="Download all files and change location in METS file after cloning")
@click.option('-l', '--download-local', is_flag=True, help="Copy all local files to workspace and change location in METS file after cloning")
@click.argument('mets_url')
@click.argument('workspace_dir', default=None, required=False)
@pass_workspace
def workspace_clone(ctx, clobber_mets, download, download_local, mets_url, workspace_dir):
    """
    Create a workspace from a METS_URL and return the directory

    METS_URL can be a URL, an absolute path or a path relative to $PWD.

    If WORKSPACE_DIR is not provided, creates a temporary directory.
    """
    workspace = ctx.resolver.workspace_from_url(
        mets_url,
        dst_dir=os.path.abspath(workspace_dir if workspace_dir else mkdtemp(prefix=TMP_PREFIX)),
        mets_basename=ctx.mets_basename,
        clobber_mets=clobber_mets,
        download=download,
        download_local=download_local,
    )
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace init
# ----------------------------------------------------------------------

@workspace_cli.command('init')
@click.option('-f', '--clobber-mets', help="Clobber mets.xml if it exists", is_flag=True, default=False)
@click.argument('directory', required=True)
@pass_workspace
def workspace_create(ctx, clobber_mets, directory):
    """
    Create a workspace with an empty METS file in DIRECTORY.

    Use '.' for $PWD"
    """
    workspace = ctx.resolver.workspace_from_nothing(
        directory=os.path.abspath(directory),
        mets_basename=ctx.mets_basename,
        clobber_mets=clobber_mets
    )
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace add
# ----------------------------------------------------------------------

@workspace_cli.command('add')
@click.option('-G', '--file-grp', help="fileGrp USE", required=True)
@click.option('-i', '--file-id', help="ID for the file", required=True)
@click.option('-m', '--mimetype', help="Media type of the file", required=True)
@click.option('-g', '--group-id', help="GROUPID")
@click.option('--force', help="If file with ID already exists, replace it", default=False, is_flag=True)
@click.argument('local_filename', type=click.Path(dir_okay=False, readable=True, resolve_path=True), required=True)
@pass_workspace
def workspace_add_file(ctx, file_grp, file_id, mimetype, group_id, force, local_filename):
    """
    Add a file LOCAL_FILENAME to METS in a workspace.
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)

    if not local_filename.startswith(ctx.directory):
        log.debug("File '%s' is not in workspace, copying", local_filename)
        local_filename = ctx.resolver.download_to_directory(ctx.directory, "file://" + local_filename, subdir=file_grp)

    url = "file://" + local_filename

    workspace.mets.add_file(
        fileGrp=file_grp,
        ID=file_id,
        mimetype=mimetype,
        url=url,
        groupId=group_id,
        force=force,
        local_filename=local_filename
    )
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace find
# ----------------------------------------------------------------------

@workspace_cli.command('find')
@click.option('-G', '--file-grp', help="fileGrp USE")
@click.option('-m', '--mimetype', help="Media type to look for")
@click.option('-g', '--group-id', help="GROUPID")
@click.option('-i', '--file-id', help="ID")
@click.option('-L', '--local-only', help="Find only file://-URL files", is_flag=True)
# pylint: disable=bad-continuation
@click.option('-k', '--output-field', help="Output field. Repeat for multiple fields, will be joined with tab",
        default=['url'],
        multiple=True,
        type=click.Choice([
            'url',
            'mimetype',
            'groupId',
            'ID',
            'basename',
            'basename_without_extension',
            'local_filename',
        ]))
@click.option('--download', is_flag=True, help="Download found files to workspace and change location in METS file ")
@pass_workspace
def workspace_find(ctx, file_grp, local_only, mimetype, group_id, file_id, output_field, download):
    """
    Find files.
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    for f in workspace.mets.find_files(
            ID=file_id,
            fileGrp=file_grp,
            local_only=local_only,
            mimetype=mimetype,
            groupId=group_id,
        ):
        if download:
            workspace.download_file(f, subdir=f.fileGrp)
            workspace.save_mets()
        ret = '\t'.join([getattr(f, field) or '' for field in output_field])
        print(ret)

# ----------------------------------------------------------------------
# ocrd workspace list-group
# ----------------------------------------------------------------------

@workspace_cli.command('list-group', help="""

    List fileGrp USE attributes

""")
@pass_workspace
def list_groups(ctx):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    print("\n".join(workspace.mets.file_groups))

# ----------------------------------------------------------------------
# ocrd workspace get-id
# ----------------------------------------------------------------------

@workspace_cli.command('get-id', help="""

    Get METS id if any

""")
@pass_workspace
def get_id(ctx):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    ID = workspace.mets.unique_identifier
    if ID:
        print(ID)

# ----------------------------------------------------------------------
# ocrd workspace set-id
# ----------------------------------------------------------------------

@workspace_cli.command('set-id', help="""

    Set METS ID.

    If one of the supported identifier mechanisms is used, will set this identifier.

    Otherwise will create a new <mods:identifier type="purl">{{ ID }}</mods:identifier>.
""")
@click.argument('ID')
@pass_workspace
def set_id(ctx, ID):
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    workspace.mets.unique_identifier = ID
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace backup
# ----------------------------------------------------------------------

@workspace_cli.group('backup')
@click.pass_context
def workspace_backup_cli(ctx): # pylint: disable=unused-argument
    """
    Backing and restoring workspaces - dev edition
    """

@workspace_backup_cli.command('add')
@pass_workspace
def workspace_backup_add(ctx):
    """
    Create a new backup
    """
    backup_manager = WorkspaceBackupManager(Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup))
    backup_manager.add()

@workspace_backup_cli.command('list')
@pass_workspace
def workspace_backup_list(ctx):
    """
    List backups
    """
    backup_manager = WorkspaceBackupManager(Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup))
    for b in backup_manager.list():
        print(b)

@workspace_backup_cli.command('restore')
@click.option('-f', '--choose-first', help="Restore first matching version if more than one", is_flag=True)
@click.argument('bak') #, type=click.Path(dir_okay=False, readable=True, resolve_path=True))
@pass_workspace
def workspace_backup_restore(ctx, choose_first, bak):
    """
    Restore backup BAK
    """
    backup_manager = WorkspaceBackupManager(Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup))
    backup_manager.restore(bak, choose_first)

@workspace_backup_cli.command('undo')
@pass_workspace
def workspace_backup_undo(ctx):
    """
    Restore the last backup
    """
    backup_manager = WorkspaceBackupManager(Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup))
    backup_manager.undo()
