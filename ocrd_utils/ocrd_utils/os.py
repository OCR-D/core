"""
Operating system functions.
"""
__all__ = [
    'abspath',
    'pushd_popd',
    'unzip_file_to_dir',
    'list_resource_candidates',
    'atomic_write',
]

from tempfile import TemporaryDirectory
import contextlib
from os import getcwd, chdir, stat, chmod, umask, environ, scandir
from pathlib import Path
from os.path import exists, abspath as abspath_, join, isdir
from zipfile import ZipFile

from atomicwrites import atomic_write as atomic_write_, AtomicWriter

from .constants import XDG_DATA_HOME

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
        oldcwd = '/tmp'
    try:
        if tempdir:
            with TemporaryDirectory() as tempcwd:
                chdir(tempcwd)
                yield tempcwd
        else:
            if newcwd:
                chdir(newcwd)
            yield newcwd
    finally:
        chdir(oldcwd)

def unzip_file_to_dir(path_to_zip, output_directory):
    """
    Extract a ZIP archive to a directory
    """
    z = ZipFile(path_to_zip, 'r')
    z.extractall(output_directory)
    z.close()

def list_resource_candidates(executable, fname, cwd=getcwd(), is_file=False, is_dir=False):
    """
    Generate candidates for processor resources according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters (except python-bundled)
    """
    candidates = []
    candidates.append(join(cwd, fname))
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in environ:
        candidates += [join(x, fname) for x in environ[processor_path_var].split(':')]
    candidates.append(join(XDG_DATA_HOME, 'ocrd-resources', executable, fname))
    candidates.append(join('/usr/local/share/ocrd-resources', executable, fname))
    if is_file:
        candidates = [c for c in candidates if Path(c).is_file()]
    if is_dir:
        candidates = [c for c in candidates if Path(c).is_dir()]
    return candidates

def list_all_resources(executable):
    """
    List all processor resources in the filesystem according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters (except python-bundled)
    """
    candidates = []
    # XXX cwd would list too many false positives
    # cwd_candidate = join(getcwd(), 'ocrd-resources', executable)
    # if Path(cwd_candidate).exists():
    #     candidates.append(cwd_candidate)
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in environ:
        for processor_path in environ[processor_path_var].split(':'):
            if isdir(processor_path):
                candidates += list(scandir(processor_path))
    datadir = join(XDG_DATA_HOME, 'ocrd-resources', executable)
    if isdir(datadir):
        candidates += list(scandir(datadir))
    systemdir = join('/usr/local/share/ocrd-resources', executable)
    if isdir(systemdir):
        candidates += list(scandir(systemdir))
    return [x.path for x in candidates]

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
