"""
Operating system functions.
"""
__all__ = [
    'abspath',
    'pushd_popd',
    'unzip_file_to_dir',
    'list_resource_candidates'
]

from tempfile import TemporaryDirectory
import contextlib
from os import getcwd, chdir
from os.path import join, expanduser, isdir, exists
import os.path
from zipfile import ZipFile

from .constants import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME

def abspath(url):
    """
    Get a full path to a file or file URL

    See os.abspath
    """
    if url.startswith('file://'):
        url = url[len('file://'):]
    return os.path.abspath(url)

@contextlib.contextmanager
def pushd_popd(newcwd=None, tempdir=False):
    if newcwd and tempdir:
        raise Exception("pushd_popd can accept either newcwd or tempdir, not both")
    try:
        oldcwd = getcwd()
    except FileNotFoundError as e:  # pylint: disable=unused-variable
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

def list_resource_candidates(executable, fname, cwd=os.getcwd()):
    """
    Generate candidates for processor resources according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters (except python-bundled)
    """
    candidates = []
    candidates.append(join(cwd, fname))
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in os.environ:
        candidates += [join(x, fname) for x in os.environ[processor_path_var].split(':')]
    if 'VIRTUAL_ENV' in os.environ:
        candidates.append(join(os.environ['VIRTUAL_ENV'], 'share', executable, fname))
    candidates.append(join(XDG_DATA_HOME, executable, fname))
    candidates.append(join(XDG_CONFIG_HOME, executable, fname))
    candidates.append(join(XDG_CACHE_HOME, executable, fname))
    return candidates

def list_all_resources(executable):
    """
    List all processor resources in the filesystem according to
    https://ocr-d.de/en/spec/ocrd_tool#file-parameters (except python-bundled)
    """
    candidates = []
    # XXX this will produce too many false positives
    # for root, dirs, files in os.walk(cwd):
    #     candidates += files
    processor_path_var = '%s_PATH' % executable.replace('-', '_').upper()
    if processor_path_var in os.environ:
        for processor_path in os.environ[processor_path_var].split(':'):
            if isdir(processor_path):
                for root, dirs, files in os.walk(processor_path):
                    candidates += files
    if 'VIRTUAL_ENV' in os.environ:
        sharedir = join(os.environ['VIRTUAL_ENV'], 'share', executable)
        if isdir(sharedir):
            for root, dirs, files in os.walk(sharedir):
                candidates += files
    for xdgdir in [join(d, executable) for d in [XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME]]:
        if isdir(xdgdir):
            for root, dirs, files in os.walk(xdgdir):
                candidates += files
    return candidates
