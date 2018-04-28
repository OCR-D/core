import os

import click

from ocrd import Resolver, WorkspaceValidator, Workspace

class WorkspaceCtx(object):

    def __init__(self, directory):
        self.directory = directory
        self.resolver = Resolver(cache_enabled=True)
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
@click.pass_context
def workspace_cli(ctx, directory, config, verbose):
    ctx.obj = WorkspaceCtx(os.path.abspath(directory))
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.config[key] = value

# ----------------------------------------------------------------------
# ocrd workspace validate
# ----------------------------------------------------------------------

@workspace_cli.command('validate', help='''

    Validate a workspace

''')
@click.option('-m', '--mets-url', help="METS URL to validate", required=True)
def validate_workspace(ctx, mets_url):
    report = WorkspaceValidator.validate_url(ctx.resolver, mets_url)
    print(report.to_xml())
    if not report.is_valid:
        return 128

# ----------------------------------------------------------------------
# ocrd workspace clone
# ----------------------------------------------------------------------

@workspace_cli.command('clone', help="""

    Create a workspace from a METS URL and return the directory

""")
@click.option('-m', '--mets-url', help="METS URL to create workspace for", required=True)
@click.option('-a', '--download-all', is_flag=True, default=False, help="Whether to download all files into the workspace")
def workspace_create(ctx, mets_url, download_all):
    workspace = ctx.resolver.workspace_from_url(mets_url)
    if download_all:
        for fileGrp in workspace.mets.file_groups:
            for f in workspace.mets.find_files(fileGrp=fileGrp):
                workspace.download_file(f, subdir=fileGrp, basename=f.ID)
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace add
# ----------------------------------------------------------------------

@workspace_cli.command('add', help="""

    Add a file to METS in a workspace.

""")
@click.option('-G', '--file-grp', help="fileGrp USE", required=True)
@click.option('-i', '--file-id', help="ID for the file")
@click.option('-g', '--group-id', help="GROUPID")
@click.argument('local_filename', type=click.Path(dir_okay=False, readable=True, resolve_path=True))
def workspace_add_file(ctx, file_grp, local_filename, file_id, group_id):
    workspace = Workspace(ctx.resolver, working_dir)
    workspace.mets.add_file(
        file_grp=file_grp,
        file_id=file_id,
        group_id=group_id,
        local_filename=local_filename
    )
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
