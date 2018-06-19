import os
import sys

import click

from ocrd import Resolver, WorkspaceValidator, Workspace

class WorkspaceCtx(object):

    def __init__(self, directory, cache_enabled):
        self.directory = directory
        self.resolver = Resolver(cache_enabled=cache_enabled)
        self.config = {}
        self.verbose = False

pass_workspace = click.make_pass_decorator(WorkspaceCtx)

# ----------------------------------------------------------------------
# ocrd workspace
# ----------------------------------------------------------------------

@click.group("workspace", help="Working with workspace")
@click.option(
    '-d',
    '--directory',
    envvar='WORKSPACE_DIR',
    default=os.path.abspath('.'),
    type=click.Path(file_okay=False),
    metavar='PATH',
    help='Changes the repository folder location.'
)
@click.option(
    '-c',
    '--config',
    nargs=2,
    multiple=True,
    metavar='KEY VALUE',
    help='Overrides a config key/value pair.'
)
@click.option(
    '-v',
    '--verbose',
    is_flag=True,
    help='Enables verbose mode.'
)
@click.option(
    '--no-cache',
    is_flag=True,
    help='Disables caching of assets.'
)
@click.pass_context
def workspace_cli(ctx, directory, config, verbose, no_cache):
    ctx.obj = WorkspaceCtx(os.path.abspath(directory), cache_enabled=not no_cache)
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.config[key] = value

# ----------------------------------------------------------------------
# ocrd workspace validate
# ----------------------------------------------------------------------

@workspace_cli.command('validate', help='''

    Validate a workspace

''')
@click.option('-m', '--mets-url', help="METS URL to validate")
@pass_workspace
def validate_workspace(ctx, mets_url=None):
    if mets_url is None:
        mets_url = 'file://%s/mets.xml' % ctx.directory
    report = WorkspaceValidator.validate_url(ctx.resolver, mets_url)
    print(report.to_xml())
    if not report.is_valid:
        sys.exit(128)

# ----------------------------------------------------------------------
# ocrd workspace clone
# ----------------------------------------------------------------------

@workspace_cli.command('clone', help="""

    Create a workspace from a METS URL and return the directory

""")
@click.option('-m', '--mets-url', help="METS URL to create workspace for", required=True)
@click.option('-a', '--download-all', is_flag=True, default=False, help="Whether to download all files into the workspace")
@pass_workspace
def workspace_clone(ctx, mets_url, download_all):
    workspace = ctx.resolver.workspace_from_url(mets_url)
    if download_all:
        for fileGrp in workspace.mets.file_groups:
            workspace.download_files_in_group(fileGrp)
            #  for f in workspace.mets.find_files(fileGrp=fileGrp):
            #      workspace.download_file(f, subdir=fileGrp, basename=f.ID)
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace create
# ----------------------------------------------------------------------

@workspace_cli.command('create', help="""

    Create a workspace with an empty METS file.

""")
@click.option('-f', '--force', help="Clobber mets.xml if it exists", is_flag=True, default=False)
@pass_workspace
def workspace_create(ctx, force):
    workspace = ctx.resolver.workspace_from_nothing(directory=ctx.directory, clobber_mets=force)
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace add
# ----------------------------------------------------------------------

@workspace_cli.command('add', help="""

    Add a file to METS in a workspace.

""")
@click.option('-G', '--file-grp', help="fileGrp USE", required=True)
@click.option('-i', '--file-id', help="ID for the file", required=True)
@click.option('-m', '--mimetype', help="Media type of the file", required=True)
@click.option('-u', '--url', help="url", default="file://local_filename")
@click.option('-g', '--group-id', help="GROUPID")
@click.argument('local_filename', type=click.Path(dir_okay=False, readable=True, resolve_path=True))
@pass_workspace
def workspace_add_file(ctx, file_grp, file_id, mimetype, url, group_id, local_filename):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    workspace.mets.add_file(
        fileGrp=file_grp,
        ID=file_id,
        mimetype=mimetype,
        url="file://" + local_filename,
        groupId=group_id,
        local_filename=local_filename
    )
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace find
# ----------------------------------------------------------------------

@workspace_cli.command('find', help="""

    Find files

""")
@click.option('-G', '--file-grp', help="fileGrp USE")
@click.option('-m', '--mimetype', help="Media type to look for")
@click.option('-g', '--group-id', help="GROUPID")
@click.option('-k', '--output-field', help="Output field", default='url', type=click.Choice([
    'url',
    'mimetype',
    'groupId',
    'ID',
    'basename',
    'basename_without_extension',
    'local_filename',
]))
@click.option('-a', '--download-all', is_flag=True, help="Whether to download found files")
@pass_workspace
def workspace_find(ctx, file_grp, mimetype, group_id, output_field, download_all):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    for f in workspace.mets.find_files(
            fileGrp=file_grp,
            mimetype=mimetype,
            groupId=group_id,
        ):
        if download_all:
            workspace.download_file(f)
        print(getattr(f, output_field))

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

    Set METS id

""")
@click.argument('ID', "Identifier")
@pass_workspace
def set_id(ctx, ID):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    workspace.mets.unique_identifier = ID
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace pack
# ----------------------------------------------------------------------

@workspace_cli.command('pack', help="""

    Pack workspace as ZIP

""")
@click.argument('output_filename', type=click.Path(dir_okay=False, writable=True, readable=False, resolve_path=True))
@pass_workspace
def pack(ctx, output_filename):
    workspace = Workspace(ctx.resolver, directory=ctx.directory)
    ctx.resolver.pack_workspace(workspace, output_filename)

# ----------------------------------------------------------------------
# ocrd workspace unpack
# ----------------------------------------------------------------------

@workspace_cli.command('unpack', help="""

    Unpack ZIP as workspace

""")
@click.argument('input_filename', type=click.Path(dir_okay=False, readable=True, resolve_path=True))
@pass_workspace
def unpack(ctx, input_filename):
    workspace = ctx.resolver.unpack_workspace_from_filename(input_filename)
    print(workspace)
