"""
Operating system functions.
"""
__all__ = [
    'abspath',
    'pushd_popd',
    'unzip_file_to_dir',
]

import contextlib
from os import getcwd, chdir
import os.path

from zipfile import ZipFile

def abspath(url):
    """
    Get a full path to a file or file URL

    See os.abspath
    """
    if url.startswith('file://'):
        url = url[len('file://'):]
    return os.path.abspath(url)

@contextlib.contextmanager
def pushd_popd(newcwd=None):
    try:
        oldcwd = getcwd()
    except FileNotFoundError as e:  # pylint: disable=unused-variable
        # This happens when a directory is deleted before the context is exited
        oldcwd = '/tmp'
    try:
        if newcwd:
            chdir(newcwd)
        yield
    finally:
        chdir(oldcwd)

def unzip_file_to_dir(path_to_zip, output_directory):
    """
    Extract a ZIP archive to a directory
    """
    z = ZipFile(path_to_zip, 'r')
    z.extractall(output_directory)
    z.close()


