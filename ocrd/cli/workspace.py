import click
from ocrd import Resolver, WorkspaceValidator, Workspace

# ----------------------------------------------------------------------
# ocrd workspace
# ----------------------------------------------------------------------

@click.group("workspace", help="Working with workspace")
def workspace_cli():
    pass

# ----------------------------------------------------------------------
# ocrd workspace validate
# ----------------------------------------------------------------------

@workspace_cli.command('validate', help='Validate a workspace')
@click.option('-m', '--mets-url', help="METS URL to validate", required=True)
def validate_workspace(mets_url):
    resolver = Resolver(cache_enabled=True)
    report = WorkspaceValidator.validate_url(resolver, mets_url)
    print(report.to_xml())
    if not report.is_valid:
        return 128

# ----------------------------------------------------------------------
# ocrd workspace create-from-url
# ----------------------------------------------------------------------

@workspace_cli.command('create-from-url', help="Create a workspace from a METS URL and return the directory")
@click.option('-m', '--mets-url', help="METS URL to create workspace for", required=True)
@click.option('-a', '--download-all', is_flag=True, default=False, help="Whether to download all files into the workspace")
def workspace_create(mets_url, download_all):
    resolver = Resolver(cache_enabled=True)
    workspace = resolver.workspace_from_url(mets_url)
    if download_all:
        for fileGrp in workspace.mets.file_groups:
            for f in workspace.mets.find_files(fileGrp=fileGrp):
                workspace.download_file(f, subdir=fileGrp, basename=f.ID)
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace add-file
# ----------------------------------------------------------------------

@workspace_cli.command('add-file', help="Add a file to METS in a workspace")
@click.option('-w', '--working-dir', help="Directory of the workspace", required=True)
@click.option('-G', '--filegrp', help="fileGrp USE", required=True)
@click.option('-i', '--fileid', help="ID for the file")
@click.option('-g', '--groupid', help="GROUPID")
@click.argument('local_filename')
def workspace_add_file(working_dir, filegrp, local_filename, fileid, groupid):
    resolver = Resolver(cache_enabled=True)
    workspace = Workspace(resolver, working_dir)
    workspace.mets.add_file(filegrp, local_filename=local_filename)
    workspace.save_mets()
