import atexit
from contextlib import ExitStack
from pathlib import Path

try:
    from importlib.resources import as_file, files
except ImportError:
    from importlib_resources import as_file, files  # type: ignore

try:
    from importlib.metadata import distribution as get_distribution
except ImportError:
    from importlib_metadata import distribution as get_distribution

# See https://importlib-resources.readthedocs.io/en/latest/migration.html#pkg-resources-resource-filename
_file_manager = ExitStack()
atexit.register(_file_manager.close)


def resource_filename(package: str, resource: str) -> Path:
    """
    Reimplementation of the function with the same name from pkg_resources

    Using importlib for better performance

    package : str
        The package from where to start looking for resource (often __name__)
    resource : str
        The resource to look up
    """
    parent_package = package.rsplit('.',1)[0]
    return _file_manager.enter_context(as_file(files(parent_package).joinpath(resource)))


def resource_string(package: str, resource: str) -> bytes:
    """
    Reimplementation of the function with the same name from pkg_resources

    Using importlib for better performance

    package : str
        The package from where to start looking for resource (often __name__)
    resource : str
        The resource to look up
    """
    parent_package = package.rsplit('.',1)[0]
    return files(parent_package).joinpath(resource).read_bytes()

__all__ = ['resource_filename', 'resource_string', 'get_distribution']
