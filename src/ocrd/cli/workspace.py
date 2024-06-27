"""
OCR-D CLI: workspace management

.. click:: ocrd.cli.workspace:workspace_cli
    :prog: ocrd workspace
    :nested: full
"""
import os
from os import getcwd, rmdir, unlink
from os.path import dirname, relpath, normpath, exists, join, isabs, isdir
from pathlib import Path
from json import loads, dumps
import sys
from glob import glob   # XXX pathlib.Path.glob does not support absolute globs
import re
import time
import numpy as np

import click

from ocrd import Resolver, Workspace, WorkspaceValidator, WorkspaceBackupManager
from ocrd.mets_server import OcrdMetsServer
from ocrd_utils import getLogger, initLogging, pushd_popd, EXT_TO_MIME, safe_filename, parse_json_string_or_file, partition_list, DEFAULT_METS_BASENAME
from ocrd.decorators import mets_find_options
from . import command_with_replaced_help
from ocrd_models.constants import METS_PAGE_DIV_ATTRIBUTE


class WorkspaceCtx():

    def __init__(self, directory, mets_url, mets_basename=DEFAULT_METS_BASENAME, mets_server_url=None, automatic_backup=False):
        self.log = getLogger('ocrd.cli.workspace')
        if mets_basename:
            self.log.warning(DeprecationWarning('--mets-basename is deprecated. Use --mets/--directory instead.'))
        self.resolver = Resolver()
        self.directory, self.mets_url, self.mets_basename, self.mets_server_url \
                = self.resolver.resolve_mets_arguments(directory, mets_url, mets_basename, mets_server_url)
        self.automatic_backup = automatic_backup


pass_workspace = click.make_pass_decorator(WorkspaceCtx)

# ----------------------------------------------------------------------
# ocrd workspace
# ----------------------------------------------------------------------

@click.group("workspace")
@click.option('-d', '--directory', envvar='WORKSPACE_DIR', type=click.Path(file_okay=False), metavar='WORKSPACE_DIR', help='Changes the workspace folder location [default: METS_URL directory or .]"')
@click.option('-M', '--mets-basename', default=None, help='METS file basename. Deprecated, use --mets/--directory')
@click.option('-m', '--mets', default=None, help='The path/URL of the METS file [default: WORKSPACE_DIR/mets.xml]', metavar="METS_URL")
@click.option('-U', '--mets-server-url', 'mets_server_url', help="TCP host URI or UDS path of METS server")
@click.option('--backup', default=False, help="Backup mets.xml whenever it is saved.", is_flag=True)
@click.pass_context
def workspace_cli(ctx, directory, mets, mets_basename, mets_server_url, backup):
    """
    Managing workspaces

    A workspace comprises a METS file and a directory as point of reference.

    Operates on the file system directly or via a METS server 
    (already running via some prior `server start` subcommand).
    """
    initLogging()
    ctx.obj = WorkspaceCtx(
        directory,
        mets_url=mets,
        mets_basename=mets_basename,
        mets_server_url=mets_server_url,
        automatic_backup=backup
    )

# ----------------------------------------------------------------------
# ocrd workspace validate
# ----------------------------------------------------------------------

@workspace_cli.command('validate', cls=command_with_replaced_help(
    (r' \[METS_URL\]', ''))) # XXX deprecated argument
@pass_workspace
@click.option('-a', '--download', is_flag=True, help="Download all files")
@click.option('-s', '--skip', help="Tests to skip", default=[], multiple=True, type=click.Choice(
    ['imagefilename', 'dimension', 'pixel_density', 'page', 'url', 'page_xsd', 'mets_fileid_page_pcgtsid',
     'mets_unique_identifier', 'mets_file_group_names', 'mets_files', 'mets_xsd']))
@click.option('--page-textequiv-consistency', '--page-strictness', help="How strict to check PAGE multi-level textequiv consistency", type=click.Choice(['strict', 'lax', 'fix', 'off']), default='strict')
@click.option('--page-coordinate-consistency', help="How fierce to check PAGE multi-level coordinate consistency", type=click.Choice(['poly', 'baseline', 'both', 'off']), default='poly')
@click.argument('mets_url', default=None, required=False)
def workspace_validate(ctx, mets_url, download, skip, page_textequiv_consistency, page_coordinate_consistency):
    """
    Validate a workspace

    METS_URL can be a URL, an absolute path or a path relative to $PWD.
    If not given, use --mets accordingly.

    Check that the METS and its referenced file contents
    abide by the OCR-D specifications.
    """
    LOG = getLogger('ocrd.cli.workspace.validate')
    if mets_url:
        LOG.warning(DeprecationWarning("Use 'ocrd workspace --mets METS init' instead of argument 'METS_URL' ('%s')" % mets_url))
    else:
        mets_url = ctx.mets_url
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

@workspace_cli.command('clone', cls=command_with_replaced_help(
    (r' \[WORKSPACE_DIR\]', ''))) # XXX deprecated argument
@click.option('-f', '--clobber-mets', help="Overwrite existing METS file", default=False, is_flag=True)
@click.option('-a', '--download', is_flag=True, help="Download all files and change location in METS file after cloning")
@click.argument('mets_url')
@mets_find_options
# XXX deprecated
@click.argument('workspace_dir', default=None, required=False)
@pass_workspace
def workspace_clone(ctx, clobber_mets, download, file_grp, file_id, page_id, mimetype, include_fileGrp, exclude_fileGrp, mets_url, workspace_dir):
    """
    Create a workspace from METS_URL and return the directory

    METS_URL can be a URL, an absolute path or a path relative to $PWD.
    If METS_URL is not provided, use --mets accordingly.
    METS_URL can also be an OAI-PMH GetRecord URL wrapping a METS file.
    """
    LOG = getLogger('ocrd.cli.workspace.clone')
    if workspace_dir:
        LOG.warning(DeprecationWarning("Use 'ocrd workspace --directory DIR clone' instead of argument 'WORKSPACE_DIR' ('%s')" % workspace_dir))
        ctx.directory = workspace_dir

    workspace = ctx.resolver.workspace_from_url(
        mets_url,
        dst_dir=ctx.directory,
        mets_basename=ctx.mets_basename,
        clobber_mets=clobber_mets,
        download=download,
        ID=file_id,
        pageId=page_id,
        mimetype=mimetype,
        include_fileGrp=include_fileGrp,
        exclude_fileGrp=exclude_fileGrp,
    )
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace init
# ----------------------------------------------------------------------

@workspace_cli.command('init', cls=command_with_replaced_help(
    (r' \[DIRECTORY\]', ''))) # XXX deprecated argument
@click.option('-f', '--clobber-mets', help="Clobber mets.xml if it exists", is_flag=True, default=False)
# XXX deprecated
@click.argument('directory', default=None, required=False)
@pass_workspace
def workspace_init(ctx, clobber_mets, directory):
    """
    Create a workspace with an empty METS file in DIRECTORY or CWD.

    """
    LOG = getLogger('ocrd.cli.workspace.init')
    if directory:
        LOG.warning(DeprecationWarning("Use 'ocrd workspace --directory DIR init' instead of argument 'DIRECTORY' ('%s')" % directory))
        ctx.directory = directory
    workspace = ctx.resolver.workspace_from_nothing(
        directory=ctx.directory,
        mets_basename=ctx.mets_basename,
        clobber_mets=clobber_mets
    )
    workspace.save_mets()
    print(workspace.directory)

# ----------------------------------------------------------------------
# ocrd workspace add
# ----------------------------------------------------------------------

@workspace_cli.command('add')
@click.option('-G', '--file-grp', help="fileGrp USE", required=True, metavar='FILE_GRP')
@click.option('-i', '--file-id', help="ID for the file", required=True, metavar='FILE_ID')
@click.option('-m', '--mimetype', help="Media type of the file. Guessed from extension if not provided", required=False, metavar='TYPE')
@click.option('-g', '--page-id', help="ID of the physical page", metavar='PAGE_ID')
@click.option('-C', '--check-file-exists', help="Whether to ensure FNAME exists", is_flag=True, default=False)
@click.option('--ignore', help="Do not check whether file exists.", default=False, is_flag=True)
@click.option('--force', help="If file with ID already exists, replace it. No effect if --ignore is set.", default=False, is_flag=True)
@click.argument('fname', required=True)
@pass_workspace
def workspace_add_file(ctx, file_grp, file_id, mimetype, page_id, ignore, check_file_exists, force, fname):
    """
    Add a file or http(s) URL FNAME to METS in a workspace.
    If FNAME is not an http(s) URL and is not a workspace-local existing file, try to copy to workspace.
    """
    workspace = Workspace(
        ctx.resolver,
        directory=ctx.directory,
        mets_basename=ctx.mets_basename,
        automatic_backup=ctx.automatic_backup,
        mets_server_url=ctx.mets_server_url,
    )

    log = getLogger('ocrd.cli.workspace.add')
    if not mimetype:
        try:
            mimetype = EXT_TO_MIME[Path(fname).suffix]
            log.info("Guessed mimetype to be %s" % mimetype)
        except KeyError:
            log.error("Cannot guess mimetype from extension '%s' for '%s'. Set --mimetype explicitly" % (Path(fname).suffix, fname))

    log.debug("Adding '%s'", fname)
    local_filename = None
    if not (fname.startswith('http://') or fname.startswith('https://')):
        if not fname.startswith(ctx.directory):
            if not isabs(fname) and exists(join(ctx.directory, fname)):
                fname = join(ctx.directory, fname)
            else:
                log.debug("File '%s' is not in workspace, copying", fname)
                try:
                    fname = ctx.resolver.download_to_directory(ctx.directory, fname, subdir=file_grp)
                except FileNotFoundError:
                    if check_file_exists:
                        log.error("File '%s' does not exist, halt execution!" % fname)
                        sys.exit(1)
        if check_file_exists and not exists(fname):
            log.error("File '%s' does not exist, halt execution!" % fname)
            sys.exit(1)
        if fname.startswith(ctx.directory):
            fname = relpath(fname, ctx.directory)
        local_filename = fname

    if not page_id:
        log.warning("You did not provide '--page-id/-g', so the file you added is not linked to a specific page.")
    kwargs = {
        'file_id': file_id,
        'mimetype': mimetype,
        'page_id': page_id,
        'force': force,
        'ignore': ignore,
        'local_filename': local_filename,
        'url': fname
    }
    workspace.add_file(file_grp, **kwargs)
    workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace bulk-add
# ----------------------------------------------------------------------

# pylint: disable=broad-except
@workspace_cli.command('bulk-add')
@click.option('-r', '--regex', help="Regular expression matching the FILE_GLOB filesystem paths to define named captures usable in the other parameters", required=True)
@click.option('-m', '--mimetype', help="Media type of the file. If not provided, guess from filename", required=False)
@click.option('-g', '--page-id', help="physical page ID of the file", required=False)
@click.option('-i', '--file-id', help="ID of the file. If not provided, derive from fileGrp and filename", required=False)
@click.option('-u', '--url', help="Remote URL of the file", required=False)
@click.option('-l', '--local-filename', help="Local filesystem path in the workspace directory (copied from source file if different)", required=False)
@click.option('-G', '--file-grp', help="File group USE of the file", required=True)
@click.option('-n', '--dry-run', help="Don't actually do anything to the METS or filesystem, just preview", default=False, is_flag=True)
@click.option('-S', '--source-path', 'src_path_option', help="File path to copy from (if different from FILE_GLOB values)", required=False)
@click.option('-I', '--ignore', help="Disable checking for existing file entries (faster)", default=False, is_flag=True)
@click.option('-f', '--force', help="Replace existing file entries with the same ID (no effect when --ignore is set, too)", default=False, is_flag=True)
@click.option('-s', '--skip', help="Skip files not matching --regex (instead of failing)", default=False, is_flag=True)
@click.argument('file_glob', nargs=-1, required=True)
@pass_workspace
def workspace_cli_bulk_add(ctx, regex, mimetype, page_id, file_id, url, local_filename, file_grp, dry_run, file_glob, src_path_option, ignore, force, skip):
    """
    Add files in bulk to an OCR-D workspace.

    FILE_GLOB can either be a shell glob expression to match file names,
    or a list of expressions or '-', in which case expressions are read from STDIN.

    After globbing, --regex is matched against each expression resulting from FILE_GLOB, and can
    define named groups reusable in the --page-id, --file-id, --mimetype, --url, --source-path and
    --file-grp options, e.g. by referencing the group name 'grp' from the regex as '{{ grp }}'.

    If the FILE_GLOB expressions do not denote the file names themselves
    (but arbitrary strings for --regex matching), then use --source-path to set
    the actual file paths to use. (This could involve fixed strings or group references.)

    \b
    Examples:
        ocrd workspace bulk-add \\
                --regex '(?P<fileGrp>[^/]+)/page_(?P<pageid>.*)\\.[^.]+' \\
                --page-id 'PHYS_{{ pageid }}' \\
                --file-grp "{{ fileGrp }}" \\
                path/to/files/*/*.*
        \b
        echo "path/to/src/file.xml SEG/page_p0001.xml" \\
        | ocrd workspace bulk-add \\
                --regex '(?P<src>.*?) (?P<fileGrp>.+?)/page_(?P<pageid>.*)\\.(?P<ext>[^\\.]*)' \\
                --file-id 'FILE_{{ fileGrp }}_{{ pageid }}' \\
                --page-id 'PHYS_{{ pageid }}' \\
                --file-grp "{{ fileGrp }}" \\
                --local-filename '{{ fileGrp }}/FILE_{{ pageid }}.{{ ext }}' \\
                -

        \b
        { echo PHYS_0001 BIN FILE_0001_BIN.IMG-wolf BIN/FILE_0001_BIN.IMG-wolf.png; \\
          echo PHYS_0001 BIN FILE_0001_BIN BIN/FILE_0001_BIN.xml; \\
          echo PHYS_0002 BIN FILE_0002_BIN.IMG-wolf BIN/FILE_0002_BIN.IMG-wolf.png; \\
          echo PHYS_0002 BIN FILE_0002_BIN BIN/FILE_0002_BIN.xml; \\
        } | ocrd workspace bulk-add -r '(?P<pageid>.*) (?P<filegrp>.*) (?P<fileid>.*) (?P<local_filename>.*)' \\
          -G '{{ filegrp }}' -g '{{ pageid }}' -i '{{ fileid }}' -S '{{ local_filename }}' -
    """
    log = getLogger('ocrd.cli.workspace.bulk-add') # pylint: disable=redefined-outer-name
    workspace = Workspace(
        ctx.resolver,
        directory=ctx.directory,
        mets_basename=ctx.mets_basename,
        automatic_backup=ctx.automatic_backup,
        mets_server_url=ctx.mets_server_url,
    )

    try:
        pat = re.compile(regex)
    except Exception as e:
        log.error("Invalid regex: %s" % e)
        sys.exit(1)

    file_paths = []
    from_stdin = file_glob == ('-',)
    if from_stdin:
        file_paths += [Path(x.strip('\n')) for x in sys.stdin.readlines()]
    else:
        for fglob in file_glob:
            expanded = glob(fglob)
            if not expanded:
                file_paths += [Path(fglob)]
            else:
                file_paths += [Path(x) for x in expanded]

    for i, file_path in enumerate(file_paths):
        log.info("[%4d/%d] %s" % (i + 1, len(file_paths), file_path))

        # match regex
        m = pat.match(str(file_path))
        if not m:
            if skip:
                continue
            log.error("File '%s' not matched by regex: '%s'" % (file_path, regex))
            sys.exit(1)
        group_dict = m.groupdict()

        # set up file info
        file_dict = {'local_filename': local_filename, 'url': url, 'mimetype': mimetype, 'file_id': file_id, 'page_id': page_id, 'file_grp': file_grp}

        # Flag to track whether 'local_filename' should be 'src'
        local_filename_is_src = False

        # expand templates
        for param_name in file_dict:
            if not file_dict[param_name]:
                if param_name == 'local_filename':
                    local_filename_is_src = True
                    continue
                elif param_name in ['mimetype', 'file_id']:
                    # auto-filled below once the other
                    # replacements have happened
                    continue
                elif param_name == 'url':
                    # Remote URL is not required
                    continue
                raise ValueError(f"OcrdFile attribute '{param_name}' unset ({file_dict})")
            for group_name in group_dict:
                file_dict[param_name] = file_dict[param_name].replace('{{ %s }}' % group_name, group_dict[group_name])

        # Where to copy from
        if src_path_option:
            src_path = src_path_option
            for group_name in group_dict:
                src_path = src_path.replace('{{ %s }}' % group_name, group_dict[group_name])
            srcpath = Path(src_path)
        else:
            srcpath = file_path

        # derive --file-id from filename if not --file-id not explicitly set
        if not file_id:
            id_field = srcpath.stem if file_path != srcpath else file_path.stem
            file_dict['file_id'] = safe_filename('%s_%s' % (file_dict['file_grp'], id_field))
        if not mimetype:
            try:
                file_dict['mimetype'] = EXT_TO_MIME[srcpath.suffix]
            except KeyError:
                log.error("Cannot guess MIME type from extension '%s' for '%s'. Set --mimetype explicitly" % (srcpath.suffix, srcpath))

        # copy files if src != url
        if local_filename_is_src:
            file_dict['local_filename'] = srcpath
        else:
            destpath = Path(workspace.directory, file_dict['local_filename'])
            if srcpath != destpath and not destpath.exists():
                log.info("cp '%s' '%s'", srcpath, destpath)
                if not dry_run:
                    if not destpath.parent.is_dir():
                        destpath.parent.mkdir()
                    destpath.write_bytes(srcpath.read_bytes())

        # Add to workspace (or not)
        fileGrp = file_dict.pop('file_grp')
        if dry_run:
            log.info('workspace.add_file(%s)' % file_dict)
        else:
            workspace.add_file(fileGrp, ignore=ignore, force=force, **file_dict)

    # save changes to disk
    workspace.save_mets()


# ----------------------------------------------------------------------
# ocrd workspace find
# ----------------------------------------------------------------------

@workspace_cli.command('find')
@mets_find_options
@click.option('-k', '--output-field', help="Output field. Repeat for multiple fields, will be joined with tab",
              default=['local_filename'],
              show_default=True,
              multiple=True,
              type=click.Choice([
                  'url',
                  'mimetype',
                  'page_id',
                  'pageId',
                  'file_id',
                  'ID',
                  'file_grp',
                  'fileGrp',
                  'basename',
                  'basename_without_extension',
                  'local_filename',
              ]))
@click.option('--download', is_flag=True, help="Download found files to workspace and change location in METS file")
@click.option('--undo-download', is_flag=True, help="Remove all downloaded files from the METS and workspace")
@click.option('--keep-files', is_flag=True, help="Do not remove downloaded files from the workspace with --undo-download")
@click.option('--wait', type=int, default=0, help="Wait this many seconds between download requests")
@pass_workspace
def workspace_find(ctx, file_grp, mimetype, page_id, file_id, output_field, include_fileGrp, exclude_fileGrp, download, undo_download, keep_files, wait):
    """
    Find files.

    (If any ``FILTER`` starts with ``//``, then its remainder
     will be interpreted as a regular expression.)
    """
    snake_to_camel = {"file_id": "ID", "page_id": "pageId", "file_grp": "fileGrp"}
    output_field = [snake_to_camel.get(x, x) for x in output_field]
    modified_mets = False
    ret = list()
    workspace = Workspace(
        ctx.resolver,
        directory=ctx.directory,
        mets_basename=ctx.mets_basename,
        mets_server_url=ctx.mets_server_url,
    )
    with pushd_popd(workspace.directory):
        for f in workspace.find_files(
                file_id=file_id,
                file_grp=file_grp,
                mimetype=mimetype,
                page_id=page_id,
                include_fileGrp=include_fileGrp,
                exclude_fileGrp=exclude_fileGrp,
            ):
            ret_entry = [f.ID if field == 'pageId' else str(getattr(f, field)) or '' for field in output_field]
            if download and not f.local_filename:
                workspace.download_file(f)
                modified_mets = True
                if wait:
                    time.sleep(wait)
            if undo_download and f.url and f.local_filename:
                ret_entry = [f'Removed local_filename {f.local_filename}']
                f.local_filename = None
                modified_mets = True
                if not keep_files:
                    ctx.log.debug("rm %s [cwd=%s]", f.local_filename, workspace.directory)
                    unlink(f.local_filename)
            ret.append(ret_entry)
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
# ocrd workspace rename-group
# ----------------------------------------------------------------------

@workspace_cli.command('rename-group')
@click.argument('OLD', nargs=1)
@click.argument('NEW', nargs=1)
@pass_workspace
def rename_group(ctx, old, new):
    """
    Rename fileGrp (USE attribute ``NEW`` to ``OLD``).
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    workspace.rename_file_group(old, new)
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
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    with pushd_popd(workspace.directory):
        for f in workspace.find_files(
            file_id=file_id,
            file_grp=file_grp,
            mimetype=mimetype,
            page_id=page_id,
        ):
            try:
                if not f.local_filename or not exists(f.local_filename):
                    workspace.mets.remove_file(f.ID)
            except Exception as e:
                ctx.log.exception("Error removing %f: %s", f, e)
                raise(e)
        workspace.save_mets()

# ----------------------------------------------------------------------
# ocrd workspace clean
# ----------------------------------------------------------------------

@workspace_cli.command('clean')
@click.option('-n', '--dry-run', help="Don't actually do anything to the filesystem, just preview", default=False, is_flag=True)
@click.option('-d', '--directories', help="Remove untracked directories in addition to untracked files", default=False, is_flag=True)
@click.argument('path_glob', nargs=-1, required=False)
@pass_workspace
def clean(ctx, dry_run, directories, path_glob):
    """
    Removes files and directories from the workspace that are not
    referenced by any mets:files.

    PATH_GLOB can be a shell glob expression to match file names,
    directory names (recursively), or plain paths. All paths are
    resolved w.r.t. the workspace.

    If no PATH_GLOB are specified, then all files and directories
    may match.
    """
    log = getLogger('ocrd.cli.workspace.clean')
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    allowed_files = [normpath(f.local_filename) for f in workspace.find_files(local_only=True)]
    allowed_files.append(relpath(workspace.mets_target, start=workspace.directory))
    allowed_dirs = set(dirname(path) for path in allowed_files)
    with pushd_popd(workspace.directory):
        if len(path_glob):
            paths = []
            for expression in path_glob:
                if isabs(expression):
                    expression = relpath(expression)
                paths += glob(expression, recursive=True) or [expression]
        else:
            paths = glob('**', recursive=True)
        file_paths = [path for path in paths if not isdir(path)]
        for path in file_paths:
            if normpath(path) in allowed_files:
                continue
            if dry_run:
                log.info('unlink(%s)' % path)
            else:
                unlink(path)
        if not directories:
            return
        dir_paths = [path for path in paths if isdir(path)]
        for path in sorted(dir_paths, key=lambda p: p.count('/'), reverse=True):
            if normpath(path) in allowed_dirs:
                continue
            if dry_run:
                log.info('rmdir(%s)' % path)
            else:
                rmdir(path)

# ----------------------------------------------------------------------
# ocrd workspace list-group
# ----------------------------------------------------------------------

@workspace_cli.command('list-group')
@pass_workspace
def list_groups(ctx):
    """
    List fileGrp USE attributes
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    print("\n".join(workspace.mets.file_groups))

# ----------------------------------------------------------------------
# ocrd workspace list-page
# ----------------------------------------------------------------------

@workspace_cli.command('list-page')
@click.option('-k', '--output-field', help="Output field. Repeat for multiple fields, will be joined with tab",
              default=['ID'],
              show_default=True,
              multiple=True,
              type=click.Choice(METS_PAGE_DIV_ATTRIBUTE.names()))
@click.option('-f', '--output-format', help="Output format", type=click.Choice(['one-per-line', 'comma-separated', 'json']), default='one-per-line')
@click.option('-D', '--chunk-number', help="Partition the return value into n roughly equally sized chunks", default=1, type=int)
@click.option('-C', '--chunk-index', help="Output the nth chunk of results, -1 for all of them.", default=None, type=int)
@click.option('-r', '--page-id-range', help="Restrict the pages to those matching the provided range, based on the @ID attribute. Separate start/end with ..")
@click.option('-R', '--numeric-range', help="Restrict the pages to those in the range, in numerical document order. Separate start/end with ..")
@pass_workspace
def list_pages(ctx, output_field, output_format, chunk_number, chunk_index, page_id_range, numeric_range):
    """
    List physical page IDs

    (If any ``FILTER`` starts with ``//``, then its remainder
     will be interpreted as a regular expression.)
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    find_kwargs = {}
    if page_id_range and 'ID' in output_field:
        find_kwargs['pageId'] = page_id_range
    page_ids = sorted({x.pageId for x in workspace.mets.find_files(**find_kwargs) if x.pageId})
    ret = []

    if output_field == ['ID']:
        ret = [[x] for x in page_ids]
    else:
        for i, page_div in enumerate(workspace.mets.get_physical_pages(for_pageIds=','.join(page_ids), return_divs=True)):
            ret.append([])
            for k in output_field:
                ret[i].append(page_div.get(k, 'None'))

    if numeric_range:
        start, end = map(int, numeric_range.split('..'))
        ret = ret[start-1:end]

    chunks = partition_list(ret, chunk_number, chunk_index)
    lines = []
    if output_format == 'one-per-line':
        for chunk in chunks:
            line_strs = []
            for entry in chunk:
                line_strs.append("\t".join(entry))
            lines.append('\n'.join(line_strs))
    elif output_format == 'comma-separated':
        for chunk in chunks:
            line_strs = []
            for entry in chunk:
                line_strs.append("\t".join(entry))
            lines.append(','.join(line_strs))
    elif output_format == 'json':
        lines.append(dumps(chunks))
    print('\n'.join(lines))

# ----------------------------------------------------------------------
# ocrd workspace get-id
# ----------------------------------------------------------------------

@workspace_cli.command('get-id')
@pass_workspace
def get_id(ctx):
    """
    Get METS id if any
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename)
    ID = workspace.mets.unique_identifier
    if ID:
        print(ID)

# ----------------------------------------------------------------------
# ocrd workspace set-id
# ----------------------------------------------------------------------

@workspace_cli.command('set-id')
@click.argument('ID')
@pass_workspace
def set_id(ctx, id):   # pylint: disable=redefined-builtin
    """
    Set METS ID.

    If one of the supported identifier mechanisms is used, will set this identifier.

    Otherwise will create a new <mods:identifier type="purl">{{ ID }}</mods:identifier>.
    """
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    workspace.mets.unique_identifier = id
    workspace.save_mets()

@workspace_cli.command('update-page')
@click.option('--set', 'attr_value_pairs', help=f"set mets:div ATTR to VALUE. possible keys: {METS_PAGE_DIV_ATTRIBUTE.names()}", metavar="ATTR VALUE", nargs=2, multiple=True)
@click.option('--order', help="[DEPRECATED - use --set ATTR VALUE", metavar='ORDER')               
@click.option('--orderlabel', help="DEPRECATED - use --set ATTR VALUE", metavar='ORDERLABEL')
@click.option('--contentids', help="DEPRECATED - use --set ATTR VALUE", metavar='ORDERLABEL')
@click.argument('PAGE_ID')
@pass_workspace
def update_page(ctx, attr_value_pairs, order, orderlabel, contentids, page_id):
    """
    Update the @ID, @ORDER, @ORDERLABEL, @LABEL or @CONTENTIDS attributes of the mets:div with @ID=PAGE_ID
    """
    update_kwargs = {k: v for k, v in attr_value_pairs}
    if order:
        update_kwargs['ORDER'] = order
    if orderlabel:
        update_kwargs['ORDERLABEL'] = orderlabel
    if contentids:
        update_kwargs['CONTENTIDS'] = contentids
    try:
        workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
        workspace.mets.update_physical_page_attributes(page_id, **update_kwargs)
        workspace.save_mets()
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)

# ----------------------------------------------------------------------
# ocrd workspace merge
# ----------------------------------------------------------------------

def _handle_json_option(ctx, param, value):
    return parse_json_string_or_file(value) if value else None

@workspace_cli.command('merge')
@click.argument('METS_PATH')
@click.option('--overwrite/--no-overwrite', is_flag=True, default=False, help="Overwrite on-disk file in case of file name conflicts with data from METS_PATH")
@click.option('--force/--no-force', is_flag=True, default=False, help="Overwrite mets:file from --mets with mets:file from METS_PATH if IDs clash")
@click.option('--copy-files/--no-copy-files', is_flag=True, help="Copy files as well", default=True, show_default=True)
@click.option('--fileGrp-mapping', help="JSON object mapping src to dest fileGrp", callback=_handle_json_option)
@click.option('--fileId-mapping', help="JSON object mapping src to dest file ID", callback=_handle_json_option)
@click.option('--pageId-mapping', help="JSON object mapping src to dest page ID", callback=_handle_json_option)
@mets_find_options
@pass_workspace
def merge(ctx, overwrite, force, copy_files, filegrp_mapping, fileid_mapping, pageid_mapping, file_grp, file_id, page_id, mimetype, include_fileGrp, exclude_fileGrp, mets_path):   # pylint: disable=redefined-builtin
    """
    Merges this workspace with the workspace that contains ``METS_PATH``

    Pass a JSON string or file to ``--fileGrp-mapping``, ``--fileId-mapping`` or ``--pageId-mapping``
    in order to rename all fileGrp, file ID or page ID values, respectively.

    The ``--file-id``, ``--page-id``, ``--mimetype`` and ``--file-grp`` options have
    the same semantics as in ``ocrd workspace find``, see ``ocrd workspace find --help``
    for an explanation.
    """
    mets_path = Path(mets_path)
    if filegrp_mapping:
        filegrp_mapping = loads(filegrp_mapping)
    workspace = Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename, automatic_backup=ctx.automatic_backup)
    other_workspace = Workspace(ctx.resolver, directory=str(mets_path.parent), mets_basename=str(mets_path.name))
    workspace.merge(
        other_workspace,
        force=force,
        overwrite=overwrite,
        copy_files=copy_files,
        fileGrp_mapping=filegrp_mapping,
        fileId_mapping=fileid_mapping,
        pageId_mapping=pageid_mapping,
        file_grp=file_grp,
        file_id=file_id,
        page_id=page_id,
        mimetype=mimetype,
        include_fileGrp=include_fileGrp,
        exclude_fileGrp=exclude_fileGrp,
    )
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


# ----------------------------------------------------------------------
# ocrd workspace server
# ----------------------------------------------------------------------

@workspace_cli.group('server')
@pass_workspace
def workspace_serve_cli(ctx): # pylint: disable=unused-argument
    """Control a METS server for this workspace"""
    assert ctx.mets_server_url, "For METS server commands, you must provide '-U/--mets-server-url'"

@workspace_serve_cli.command('stop')
@pass_workspace
def workspace_serve_stop(ctx): # pylint: disable=unused-argument
    """Stop the METS server"""
    workspace = Workspace(
        ctx.resolver,
        directory=ctx.directory,
        mets_basename=ctx.mets_basename,
        mets_server_url=ctx.mets_server_url,
    )
    workspace.mets.stop()

@workspace_serve_cli.command('start')
@pass_workspace
def workspace_serve_start(ctx): # pylint: disable=unused-argument
    """
    Start a METS server

    (For TCP backend, pass a network interface to bind to as the '-U/--mets-server-url' parameter.)
    """
    OcrdMetsServer(
        workspace=Workspace(ctx.resolver, directory=ctx.directory, mets_basename=ctx.mets_basename),
        url=ctx.mets_server_url,
    ).startup()
