import os
from os.path import relpath, exists, join
import sys

import click

from ocrd import Resolver, Workspace, WorkspaceValidator, WorkspaceBackupManager
from ocrd_utils import getLogger, pushd_popd

log = getLogger('ocrd.cli.workspace')

class WorkspaceCtx():

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
@click.option('-s', '--skip', help="Tests to skip", default=[], multiple=True, type=click.Choice(['imagefilename', 'dimension', 'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'pixel_density', 'page', 'url']))
@click.option('--page-textequiv-consistency', '--page-strictness', help="How strict to check PAGE multi-level textequiv consistency", type=click.Choice(['strict', 'lax', 'fix', 'off']), default='strict')
@click.option('--page-coordinate-consistency', help="How fierce to check PAGE multi-level coordinate consistency", type=click.Choice(['poly', 'baseline', 'both', 'off']), default='poly')
@click.argument('mets_url', nargs=-1)
def validate_workspace(ctx, mets_url, download, skip, page_textequiv_consistency, page_coordinate_consistency):
    if not mets_url:
        mets_url = 'mets.xml'
    else:
        mets_url = mets_url[0]
    report = WorkspaceValidator.validate(
        ctx.resolver,
        mets_url,
        src_dir=ctx.directory,
        skip=skip,
        download=download,
        page_strictness=page_textequiv_consistency,
        page_coordinate_consistency=page_coordinate_consistency
    )
    print(report.to_xml())
    if not report.is_valid:
        sys.exit(128)

# ----------------------------------------------------------------------
# ocrd workspace clone
# ----------------------------------------------------------------------

@workspace_cli.command('clone')
@click.option('-f', '--clobber-mets', help="Overwrite existing METS file", default=False, is_flag=True)
@click.option('-a', '--download', is_flag=True, help="Download all files and change location in METS file after cloning")
@click.argument('mets_url')
@click.argument('workspace_dir', default=None, required=False)
@pass_workspace
def workspace_clone(ctx, clobber_mets, download, mets_url, workspace_dir):
    """
    Create a workspace from a METS_URL and return the directory

    METS_URL can be a URL, an absolute path or a path relative to $PWD.

    If WORKSPACE_DIR is not provided, use the current working directory
    """
    if not workspace_dir:
        workspace_dir = '.'
    workspace = ctx.resolver.workspace_from_url(
        mets_url,
        dst_dir=os.path.abspath(workspace_dir),
        mets_basename=ctx.mets_basename,
        clobber_mets=clobber_mets,
        download=download,
    )
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace init
# ----------------------------------------------------------------------

@workspace_cli.command('init')
@click.option('-f', '--clobber-mets', help="Clobber mets.xml if it exists", is_flag=True, default=False)
@click.argument('directory', required=False)
@pass_workspace
def workspace_create(ctx, clobber_mets, directory):
    """
    Create a workspace with an empty METS file in DIRECTORY.

    Use '.' for $PWD"
    """
    if not directory:
        directory = '.'
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
@click.option('-g', '--page-id', help="ID of the physical page")
@click.option('-C', '--check-file-exists', help="Whether to ensure FNAME exists", is_flag=True, default=False)
@click.option('--force', help="If file with ID already exists, replace it", default=False, is_flag=True)
@click.argument('fname', required=True)
@pass_workspace
def workspace_add_file(ctx, file_grp, file_id, mimetype, page_id, check_file_exists, force, fname):
    """
    Add a file or http(s) URL FNAME to METS in a workspace.
    If FNAME is not an http(s) URL and is not a workspace-local existing file, try to copy to workspace.
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)

    kwargs = {'fileGrp': file_grp, 'ID': file_id, 'mimetype': mimetype, 'pageId': page_id, 'force': force}
    log = getLogger('ocrd.cli.workspace.add')
    if not (fname.startswith('http://') or fname.startswith('https://')):
        if not fname.startswith(ctx.directory):
            if exists(join(ctx.directory, fname)):
                fname = join(ctx.directory, fname)
            else:
                log.debug("File '%s' is not in workspace, copying", fname)
                try:
                    fname = ctx.resolver.download_to_directory(ctx.directory, fname, subdir=file_grp)
                except FileNotFoundError as e:
                    if check_file_exists:
                        log.error("File '%s' does not exist, halt execution!" % fname)
                        sys.exit(1)
        if check_file_exists and not exists(fname):
            log.error("File '%s' does not exist, halt execution!" % fname)
            sys.exit(1)
        if fname.startswith(ctx.directory):
            fname = relpath(fname, ctx.directory)
        kwargs['local_filename'] = fname

    kwargs['url'] = fname
    workspace.mets.add_file(**kwargs)
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace find
# ----------------------------------------------------------------------

@workspace_cli.command('find')
@click.option('-G', '--file-grp', help="fileGrp USE", metavar='FILTER')
@click.option('-m', '--mimetype', help="Media type to look for", metavar='FILTER')
@click.option('-g', '--page-id', help="Page ID", metavar='FILTER')
@click.option('-i', '--file-id', help="ID", metavar='FILTER')
# pylint: disable=bad-continuation
@click.option('-k', '--output-field', help="Output field. Repeat for multiple fields, will be joined with tab",
        default=['url'],
        multiple=True,
        type=click.Choice([
            'url',
            'mimetype',
            'pageId',
            'ID',
            'fileGrp',
            'basename',
            'basename_without_extension',
            'local_filename',
        ]))
@click.option('--download', is_flag=True, help="Download found files to workspace and change location in METS file ")
@pass_workspace
def workspace_find(ctx, file_grp, mimetype, page_id, file_id, output_field, download):
    """
    Find files.

    (If any ``FILTER`` starts with ``//``, then its remainder
     will be interpreted as a regular expression.)
    """
    modified_mets = False
    ret = list()
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    for f in workspace.mets.find_files(
            ID=file_id,
            fileGrp=file_grp,
            mimetype=mimetype,
            pageId=page_id,
        ):
        if download and not f.local_filename:
            workspace.download_file(f)
            modified_mets = True
        ret.append([f.ID if field == 'pageId' else getattr(f, field) or ''
                    for field in output_field])
    if modified_mets:
        workspace.save_mets()
    if 'pageId' in output_field:
        idx = output_field.index('pageId')
        fileIds = list(map(lambda fields: fields[idx], ret))
        pages = workspace.mets.get_physical_pages(for_fileIds=fileIds)
        for fields, page in zip(ret, pages):
            fields[idx] = page or ''
    for fields in ret:
        print('\t'.join(fields))

# ----------------------------------------------------------------------
# ocrd workspace remove
# ----------------------------------------------------------------------

@workspace_cli.command('remove')
@click.option('-k', '--keep-file', help="Do not delete file from file system", default=False, is_flag=True)
@click.option('-f', '--force', help="Continue even if mets:file or file on file system does not exist", default=False, is_flag=True)
@click.argument('ID', nargs=-1)
@pass_workspace
def workspace_remove_file(ctx, id, force, keep_file):  # pylint: disable=redefined-builtin
    """
    Delete files (given by their ID attribute ``ID``).
    
    (If any ``ID`` starts with ``//``, then its remainder
     will be interpreted as a regular expression.)
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    for i in id:
        workspace.remove_file(i, force=force, keep_file=keep_file)
    workspace.save_mets()


# ----------------------------------------------------------------------
# ocrd workspace remove-group
# ----------------------------------------------------------------------

@workspace_cli.command('remove-group')
@click.option('-r', '--recursive', help="Delete any files in the group before the group itself", default=False, is_flag=True)
@click.option('-f', '--force', help="Continue removing even if group or containing files not found in METS", default=False, is_flag=True)
@click.option('-k', '--keep-files', help="Do not delete files from file system", default=False, is_flag=True)
@click.argument('GROUP', nargs=-1)
@pass_workspace
def remove_group(ctx, group, recursive, force, keep_files):
    """
    Delete fileGrps (given by their USE attribute ``GROUP``).
    
    (If any ``GROUP`` starts with ``//``, then its remainder
     will be interpreted as a regular expression.)
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    for g in group:
        workspace.remove_file_group(g, recursive=recursive, force=force, keep_files=keep_files)
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace prune-files
# ----------------------------------------------------------------------

@workspace_cli.command('prune-files')
@click.option('-G', '--file-grp', help="fileGrp USE", metavar='FILTER')
@click.option('-m', '--mimetype', help="Media type to look for", metavar='FILTER')
@click.option('-g', '--page-id', help="Page ID", metavar='FILTER')
@click.option('-i', '--file-id', help="ID", metavar='FILTER')
@pass_workspace
def prune_files(ctx, file_grp, mimetype, page_id, file_id):
    """
    Removes mets:files that point to non-existing local files

    (If any ``FILTER`` starts with ``//``, then its remainder
     will be interpreted as a regular expression.)
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    with pushd_popd(workspace.directory):
        for f in workspace.mets.find_files(
            ID=file_id,
            fileGrp=file_grp,
            mimetype=mimetype,
            pageId=page_id,
        ):
            try:
                if not f.local_filename or not exists(f.local_filename):
                    workspace.mets.remove_file(f.ID)
            except Exception as e:
                log.exception("Error removing %f: %s", f, e)
                raise(e)
        workspace.save_mets()

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
# ocrd workspace list-pages
# ----------------------------------------------------------------------

@workspace_cli.command('list-page', help="""

    List page IDs

""")
@pass_workspace
def list_pages(ctx):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    print("\n".join(workspace.mets.physical_pages))

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
def set_id(ctx, id):   # pylint: disable=redefined-builtin
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    workspace.mets.unique_identifier = id
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
