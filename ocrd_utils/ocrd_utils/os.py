"""
Operating system functions.
"""
__all__ = [
    'abspath',
    'directory_size',
    'is_file_in_directory',
    'get_ocrd_tool_json',
    'get_moduledir',
    'get_processor_resource_types',
    'pushd_popd',
    'unzip_file_to_dir',
    'atomic_write',
]

from tempfile import TemporaryDirectory, gettempdir
from functools import lru_cache
import contextlib
from distutils.spawn import find_executable as which
from json import loads
from json.decoder import JSONDecodeError
from os import getcwd, chdir, stat, chmod, umask, environ
from pathlib import Path
from os.path import exists, abspath as abspath_, join, isdir
from zipfile import ZipFile
from subprocess import run, PIPE

from atomicwrites import atomic_write as atomic_write_, AtomicWriter

from .constants import XDG_DATA_HOME
from .logging import getLogger

def abspath(url):
    """
    Get a full path to a file or file URL

    See os.abspath
    """
    if url.startswith('file://'):
        url = url[len('file://'):]
    return abspath_(url)

@contextlib.contextmanager
def pushd_popd(newcwd=None, tempdir=False):
    if newcwd and tempdir:
        raise Exception("pushd_popd can accept either newcwd or tempdir, not both")
    try:
        oldcwd = getcwd()
    except FileNotFoundError:
        # This happens when a directory is deleted before the context is exited
        oldcwd = gettempdir()
    try:
        if tempdir:
            with TemporaryDirectory() as tempcwd:
                chdir(tempcwd)
                yield Path(tempcwd).resolve()
        else:
            if newcwd:
                chdir(newcwd)
            yield Path(newcwd).resolve()
    finally:
        chdir(oldcwd)

def unzip_file_to_dir(path_to_zip, output_directory):
    """
    Extract a ZIP archive to a directory
    """
    z = ZipFile(path_to_zip, 'r')
    z.extractall(output_directory)
    z.close()

@lru_cache()
def get_ocrd_tool_json(executable):
    """
    Get the ``ocrd-tool`` description of ``executable``.
    """
    executable_name = Path(executable).name
    try:
        ocrd_tool = loads(run([executable, '--dump-json'], stdout=PIPE).stdout)
    except (JSONDecodeError, OSError) as e:
        getLogger('ocrd_utils.get_ocrd_tool_json').error(f'{executable} --dump-json produced invalid JSON: {e}')
        ocrd_tool = {}
    if 'resource_locations' not in ocrd_tool:
        ocrd_tool['resource_locations'] = ['data', 'cwd', 'system', 'module']
    return ocrd_tool

@lru_cache()
def get_moduledir(executable):
    moduledir = None
    try:
        moduledir = run([executable, '--dump-module-dir'], encoding='utf-8', stdout=PIPE).stdout.rstrip('\n')
    except (JSONDecodeError, OSError) as e:
        getLogger('ocrd_utils.get_moduledir').error(f'{executable} --dump-module-dir failed: {e}')
    return moduledir

def list_resource_candidates(executable, fname, cwd=getcwd(), moduled=None, xdg_data_home=None):
    """
    Generate candidates for processor resources according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters
    """
    candidates = []
    candidates.append(join(cwd, fname))
    xdg_data_home = XDG_DATA_HOME if not xdg_data_home else xdg_data_home
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in environ:
        candidates += [join(x, fname) for x in environ[processor_path_var].split(':')]
    candidates.append(join(xdg_data_home, 'ocrd-resources', executable, fname))
    candidates.append(join('/usr/local/share/ocrd-resources', executable, fname))
    if moduled:
        candidates.append(join(moduled, fname))
    return candidates

def list_all_resources(executable, moduled=None, xdg_data_home=None):
    """
    List all processor resources in the filesystem according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters
    """
    candidates = []
    try:
        resource_locations = get_ocrd_tool_json(executable)['resource_locations']
    except FileNotFoundError:
        # processor we're looking for ressource_locations of is not installed.
        # Assume the default
        resource_locations = ['data', 'cwd', 'system', 'module']
    xdg_data_home = XDG_DATA_HOME if not xdg_data_home else xdg_data_home
    # XXX cwd would list too many false positives
    # if 'cwd' in resource_locations:
    #     cwd_candidate = join(getcwd(), 'ocrd-resources', executable)
    #     if Path(cwd_candidate).exists():
    #         candidates.append(cwd_candidate)
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in environ:
        for processor_path in environ[processor_path_var].split(':'):
            if Path(processor_path).is_dir():
                candidates += Path(processor_path).iterdir()
    if 'data' in resource_locations:
        datadir = Path(xdg_data_home, 'ocrd-resources', executable)
        if datadir.is_dir():
            candidates += datadir.iterdir()
    if 'system' in resource_locations:
        systemdir = Path('/usr/local/share/ocrd-resources', executable)
        if systemdir.is_dir():
            candidates += systemdir.iterdir()
    if 'module' in resource_locations and moduled:
        # recurse fully
        for resource in itertree(Path(moduled)):
            if resource.is_dir():
                continue
            if any(resource.match(pattern) for pattern in
                   # Python distributions do not distinguish between
                   # code and data; `is_resource()` only singles out
                   # files over directories; but we want data files only
                   # todo: more code and cache exclusion patterns!
                   ['*.py', '*.py[cod]', '*~', 'ocrd-tool.json', 
                    'environment.pickle', 'resource_list.yml', 'lib.bash']):
                continue
            candidates.append(resource)
    # recurse once
    for parent in candidates:
        if parent.is_dir() and parent.name != '.git':
            candidates += parent.iterdir()
    return sorted([str(x) for x in candidates])

def get_processor_resource_types(executable, ocrd_tool=None):
    """
    Determine what type of resource parameters a processor needs.

    Return a list of MIME types (with the special value `*/*` to
    designate that arbitrary files or directories are allowed).
    """
    if not ocrd_tool:
        # if the processor in question is not installed, assume both files and directories
        if not which(executable):
            return ['*/*']
        ocrd_tool = get_ocrd_tool_json(executable)
    if not next((True for p in ocrd_tool.get('parameters', {}).values() if 'content-type' in p), False):
        # None of the parameters for this processor are resources (or not
        # the resource parametrs are not properly declared, so output both
        # directories and files
        return ['*/*']
    return [p['content-type'] for p in ocrd_tool['parameters'].values()
            if 'content-type' in p]

# ht @pabs3
# https://github.com/untitaker/python-atomicwrites/issues/42
class AtomicWriterPerms(AtomicWriter):
    def get_fileobject(self, **kwargs):
        f = super().get_fileobject(**kwargs)
        try:
            mode = stat(self._path).st_mode
        except FileNotFoundError:
            # Creating a new file, emulate what os.open() does
            mask = umask(0)
            umask(mask)
            mode = 0o664 & ~mask
        fd = f.fileno()
        chmod(fd, mode)
        return f

@contextlib.contextmanager
def atomic_write(fpath):
    with atomic_write_(fpath, writer_cls=AtomicWriterPerms, overwrite=True) as f:
        yield f


def is_file_in_directory(directory, file):
    """
    Return True if ``file`` is in ``directory`` (by checking that all components of ``directory`` are in ``file.parts``)
    """
    directory = Path(directory)
    file = Path(file)
    return list(file.parts)[:len(directory.parts)] == list(directory.parts)

def itertree(path):
    """
    Generate a list of paths by recursively enumerating ``path``
    """
    if not isinstance(path, Path):
        path = Path(path)
    if path.is_dir():
        for subpath in path.iterdir():
            yield from itertree(subpath)
    yield path

def directory_size(path):
    """
    Calculcates size of all files in directory ``path``
    """
    path = Path(path)
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
