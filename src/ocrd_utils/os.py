"""
Operating system functions.
"""
__all__ = [
    'abspath',
    'directory_size',
    'is_file_in_directory',
    'is_git_url',
    'get_ocrd_tool_json',
    'get_moduledir',
    'get_processor_resource_types',
    'get_env_locations',
    'guess_media_type',
    'pushd_popd',
    'unzip_file_to_dir',
    'atomic_write',
    'redirect_stderr_and_stdout_to_file',
]

from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
from tempfile import TemporaryDirectory, gettempdir
from functools import lru_cache
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from shutil import which
from json import loads
from json.decoder import JSONDecodeError
from os import getcwd, chdir, stat, chmod, umask, environ, PathLike
from pathlib import Path
from os.path import abspath as abspath_, join
from zipfile import ZipFile
from subprocess import run, PIPE, CalledProcessError
from mimetypes import guess_type as mimetypes_guess
from filetype import guess as filetype_guess
from fnmatch import filter as apply_glob

from atomicwrites import atomic_write as atomic_write_, AtomicWriter

from .constants import EXT_TO_MIME, MIME_TO_EXT, RESOURCE_LOCATIONS, RESOURCES_DIR_SYSTEM
from .config import config
from .logging import getLogger
from .introspect import resource_string

def abspath(url : str) -> str:
    """
    Get a full path to a file or file URL

    See os.abspath
    """
    if url.startswith('file://'):
        url = url[len('file://'):]
    return abspath_(url)


@contextmanager
def pushd_popd(newcwd : Union[str, PathLike] = None, tempdir : bool = False) -> Iterator[PathLike]:
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

def unzip_file_to_dir(path_to_zip : Union[str, PathLike], output_directory : str) -> None:
    """
    Extract a ZIP archive to a directory
    """
    with ZipFile(path_to_zip, 'r') as z:
        z.extractall(output_directory)


@lru_cache()
def is_git_url(url: str) -> bool:
    try:
        run(['git', 'ls-remote', '--exit-code', '-q', '-h', url], check=True)
    except CalledProcessError:
        return False
    return True


@lru_cache()
def get_ocrd_tool_json(executable : str) -> Dict[str, Any]:
    """
    Get the ``ocrd-tool`` description of ``executable``.
    """
    ocrd_tool = {}
    try:
        ocrd_all_tool = loads(resource_string('ocrd', 'ocrd-all-tool.json'))
        ocrd_tool = ocrd_all_tool[executable]
    except (JSONDecodeError, OSError, KeyError):
        try:
            ocrd_tool = loads(run([executable, '--dump-json'], stdout=PIPE, check=False).stdout)
        except (JSONDecodeError, OSError) as e:
            getLogger('ocrd.utils.get_ocrd_tool_json').error(f'{executable} --dump-json produced invalid JSON: {e}')
    if 'resource_locations' not in ocrd_tool:
        ocrd_tool['resource_locations'] = RESOURCE_LOCATIONS
    return ocrd_tool


@lru_cache()
def get_moduledir(executable : str) -> str:
    moduledir = None
    try:
        ocrd_all_moduledir = loads(resource_string('ocrd', 'ocrd-all-module-dir.json'))
        moduledir = ocrd_all_moduledir[executable]
    except (JSONDecodeError, OSError, KeyError):
        try:
            moduledir = run([executable, '--dump-module-dir'], encoding='utf-8', stdout=PIPE, check=False).stdout.rstrip('\n')
        except (JSONDecodeError, OSError) as e:
            getLogger('ocrd.utils.get_moduledir').error(f'{executable} --dump-module-dir failed: {e}')
    return moduledir

def get_env_locations(executable: str) -> List[str]:
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in environ:
        return environ[processor_path_var].split(':')
    return []

def list_resource_candidates(executable : str, fname : str, cwd : Optional[str] = None, moduled : Optional[str] = None, xdg_data_home : Optional[str] = None) -> List[str]:
    """
    Generate candidates for processor resources according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters
    """
    if cwd is None:
        cwd = getcwd()
    candidates = []
    candidates.append(join(cwd, fname))
    xdg_data_home = xdg_data_home or config.XDG_DATA_HOME
    for processor_path in get_env_locations(executable):
        candidates.append(join(processor_path, fname))
    candidates.append(join(xdg_data_home, 'ocrd-resources', executable, fname))
    candidates.append(join(RESOURCES_DIR_SYSTEM, executable, fname))
    if moduled:
        candidates.append(join(moduled, fname))
    return candidates

def list_all_resources(executable : str, ocrd_tool : Optional[Dict[str, Any]] = None, moduled : Optional[str] = None, xdg_data_home : Optional[str] = None) -> List[str]:
    """
    List all processor resources in the filesystem according to
    https://ocr-d.de/en/spec/ocrd_tool#resource-parameters
    """
    xdg_data_home = xdg_data_home or config.XDG_DATA_HOME
    if ocrd_tool is None:
        ocrd_tool = get_ocrd_tool_json(executable)
    # processor we're looking for might not be installed, hence the fallbacks
    try:
        mimetypes = get_processor_resource_types(executable, ocrd_tool=ocrd_tool)
    except KeyError:
        mimetypes = ['*/*']
    try:
        resource_locations = ocrd_tool['resource_locations']
    except KeyError:
        # Assume the default
        resource_locations = RESOURCE_LOCATIONS
    try:
        # fixme: if resources_list contains directories, their "suffix" will interfere
        # (e.g. dirname without dot means we falsely match files without suffix)
        resource_suffixes = [Path(res['name']).suffix
                             for res in ocrd_tool['resources']]
    except KeyError:
        resource_suffixes = []
    logger = getLogger('ocrd.utils.list_all_resources')
    candidates = []
    # cwd would list too many false positives:
    # if 'cwd' in resource_locations:
    #     cwddir = Path.cwd()
    #     candidates.append(cwddir.itertree())
    # but we do not use this anyway:
    # relative paths are tried w.r.t. CWD
    # prior to list_all_resources resolution.
    for processor_path in get_env_locations(executable):
        processor_path = Path(processor_path)
        if processor_path.is_dir():
            candidates += processor_path.iterdir()
    if 'data' in resource_locations:
        datadir = Path(xdg_data_home, 'ocrd-resources', executable)
        if datadir.is_dir():
            candidates += datadir.iterdir()
    if 'system' in resource_locations:
        systemdir = Path(RESOURCES_DIR_SYSTEM, executable)
        if systemdir.is_dir():
            candidates += systemdir.iterdir()
    if 'module' in resource_locations and moduled:
        # recurse fully
        moduled = Path(moduled)
        for resource in moduled.iterdir():
            if resource.is_dir():
                continue
            if any(resource.match(pattern) for pattern in
                   # Python distributions do not distinguish between
                   # code and data; `is_resource()` only singles out
                   # files over directories; but we want data files only
                   # todo: more code and cache exclusion patterns!
                   ['*.py', '*.py[cod]', '*~', '.*.swp', '*.swo',
                    '__pycache__/*', '*.egg-info/*', '*.egg',
                    'copyright.txt', 'LICENSE*', 'README.md', 'MANIFEST',
                    'TAGS', '.DS_Store',
                    # C extensions
                    '*.so',
                    # translations
                    '*.mo', '*.pot',
                    '*.log', '*.orig', '*.BAK',
                    '.git/*',
                    # our stuff
                    'ocrd-tool.json',
                    'environment.pickle', 'resource_list.yml']):
                logger.debug("ignoring module candidate '%s'", resource)
                continue
            candidates.append(resource)
    if mimetypes != ['*/*']:
        logger.debug("matching candidates for %s by content-type %s", executable, str(mimetypes))
    def valid_resource_type(path):
        if '*/*' in mimetypes:
            return True
        if path.is_dir():
            if not 'text/directory' in mimetypes:
                logger.debug("ignoring directory candidate '%s'", path)
                return False
            if path.name in ['.git']:
                logger.debug("ignoring directory candidate '%s'", path)
                return False
            return True
        if not path.is_file():
            logger.warning("ignoring non-file, non-directory candidate '%s'", path)
            return False
        res_mimetype = guess_media_type(path, fallback='')
        if res_mimetype == 'application/json':
            # always accept, regardless of configured mimetypes:
            # needed for distributing or sharing parameter preset files
            return True
        if ['text/directory'] == mimetypes:
            logger.debug("ignoring non-directory candidate '%s'", path)
            return False
        if 'application/octet-stream' in mimetypes:
            # catch-all type - do not enforce anything
            return True
        if path.suffix in resource_suffixes:
            return True
        if any(path.suffix == MIME_TO_EXT.get(mime, None)
               for mime in mimetypes):
            return True
        if not res_mimetype:
            logger.warning("cannot determine content type of candidate '%s'", path)
            return True
        if any(apply_glob([res_mimetype], mime)
               for mime in mimetypes):
            return True
        logger.debug("ignoring %s candidate '%s'", res_mimetype, path)
        return False
    candidates = sorted(filter(valid_resource_type, candidates))
    return map(str, candidates)

def get_processor_resource_types(executable : str, ocrd_tool : Optional[Dict[str, Any]] = None) -> List[str]:
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
    mime_types = [mime
                  for param in ocrd_tool.get('parameters', {}).values()
                  if param['type'] == 'string' and param.get('format', '') == 'uri' and 'content-type' in param
                  for mime in param['content-type'].split(',')]
    if not len(mime_types):
        # None of the parameters for this processor are resources
        # (or the parameters' resource types are not properly declared,)
        # so output both directories and files
        return ['*/*']
    return mime_types


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


@contextmanager
def atomic_write(fpath : str) -> Iterator[str]:
    with atomic_write_(fpath, writer_cls=AtomicWriterPerms, overwrite=True) as f:
        yield f


def is_file_in_directory(directory : Union[str, PathLike], file : Union[str, PathLike]) -> bool:
    """
    Return True if ``file`` is in ``directory`` (by checking that all components of ``directory`` are in ``file.parts``)
    """
    directory = Path(directory)
    file = Path(file)
    return list(file.parts)[:len(directory.parts)] == list(directory.parts)

def itertree(path : Union[str, PathLike]) -> PathLike:
    """
    Generate a list of paths by recursively enumerating ``path``
    """
    if not isinstance(path, Path):
        path = Path(path)
    if path.is_dir():
        for subpath in path.iterdir():
            yield from itertree(subpath)
    yield path

def directory_size(path : Union[str, PathLike]) -> int:
    """
    Calculates size of all files in directory ``path``
    """
    path = Path(path)
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

def guess_media_type(input_file : str, fallback : Optional[str] = None, application_xml : str = 'application/xml') -> str:
    """
    Guess the media type of a file path
    """
    mimetype = filetype_guess(input_file)
    if mimetype is not None:
        mimetype = mimetype.mime
    else:
        mimetype = mimetypes_guess(input_file)[0]
    if mimetype is None:
        mimetype = EXT_TO_MIME.get(''.join(Path(input_file).suffixes), fallback)
    if mimetype is None:
        raise ValueError("Could not determine MIME type of input_file '%s'", str(input_file))
    if mimetype == 'application/xml':
        mimetype = application_xml
    return mimetype


@contextmanager
def redirect_stderr_and_stdout_to_file(filename):
    with open(filename, 'at', encoding='utf-8') as f:
        with redirect_stderr(f), redirect_stdout(f):
            yield
