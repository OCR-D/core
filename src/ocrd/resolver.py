from tempfile import mkdtemp
from pathlib import Path
from warnings import warn

import requests
from requests.adapters import HTTPAdapter, Retry

from ocrd.constants import TMP_PREFIX
from ocrd_utils import (
    config,
    DEFAULT_METS_BASENAME,
    getLogger,
    is_local_filename,
    get_local_filename,
    remove_non_path_from_url,
    is_file_in_directory,
    nth_url_segment
)
from ocrd.workspace import Workspace
from ocrd_models import OcrdMets
from ocrd_models.constants import NAMESPACES as NS
from ocrd_models.utils import handle_oai_response

class Resolver():
    """
    Handle uploads, downloads, repository access, and manage temporary directories
    """

    def download_to_directory(self, directory, url, basename=None, if_exists='skip', subdir=None, retries=None, timeout=None):
        """
        Download a URL ``url`` to a local file in ``directory``.

        If ``url`` looks like a file path, check whether that exists.
        If it does exist and is within ``directory` already, return early.
        If it does exist but is outside of ``directory``. copy it.
        If ``url` does not appear to be a file path, try downloading via HTTP, retrying ``retries`` times with timeout ``timeout`` between calls.

        If ``basename`` is not given but ``subdir`` is, set ``basename`` to the last path segment of ``url``.

        If the target file already exists within ``directory``, behavior depends on ``if_exists``:
            - ``skip`` (default): do nothing and return early. Note that this
            - ``overwrite``: overwrite the existing file
            - ``raise``: raise a ``FileExistsError``

        Args:
            directory (string): Directory to download files to
            url (string): URL to download from

        Keyword Args:
            basename (string, None): basename part of the filename on disk. Defaults to last path segment of ``url`` if unset.
            if_exists (string, "skip"): What to do if target file already exists.
                One of ``skip`` (default), ``overwrite`` or ``raise``
            subdir (string, None): Subdirectory to create within the directory. Think ``mets:fileGrp[@USE]``.
            retries (int, None): Number of retries to attempt on network failure.
            timeout (tuple, None): Timeout in seconds for establishing a connection and reading next chunk of data.

        Returns:
            Local filename string, *relative* to directory
        """
        log = getLogger('ocrd.resolver.download_to_directory') # pylint: disable=redefined-outer-name
        log.debug("directory=|%s| url=|%s| basename=|%s| if_exists=|%s| subdir=|%s|", directory, url, basename, if_exists, subdir)

        if not url:
            raise ValueError(f"'url' must be a non-empty string, not '{url}'") # actually Path also ok
        if not directory:
            raise ValueError(f"'directory' must be a non-empty string, not '{url}'")  # actually Path would also work

        url = str(url)
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        subdir_path = Path(subdir if subdir else '')
        basename_path = Path(basename if basename else nth_url_segment(url))
        ret = Path(subdir_path, basename_path)
        dst_path = Path(directory, ret)

        # log.info("\n\tdst_path='%s \n\turl=%s", dst_path, url)
        # print(f'>>> url={url}')
        # print(f'>>> directory={directory}')
        # print(f'>>> subdir_path={subdir_path}')
        # print(f'>>> basename_path={basename_path}')
        # print(f'>>> dst_path={dst_path}')
        # print(f'>>> ret={ret}')

        src_path = None
        if is_local_filename(url):
            try:
                src_path = Path(get_local_filename(url)).resolve()
            except FileNotFoundError as e:
                log.error("Failed to resolve URL locally: %s --> '%s' which does not exist" % (url, src_path))
                raise e
            if not src_path.exists():
                raise FileNotFoundError(f"File path passed as 'url' to download_to_directory does not exist: '{url}")
            if src_path == dst_path:
                log.debug("Stop early, src_path and dst_path are the same: '%s' (url: '%s')" % (src_path, url))
                return str(ret)

        # Respect 'if_exists' arg
        if dst_path.exists():
            if if_exists == 'skip':
                return str(ret)
            if if_exists == 'raise':
                raise FileExistsError(f"File already exists and if_exists == 'raise': {dst_path}")

        # Create dst_path parent dir
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy files or download remote assets
        if src_path:
            # src_path set, so it is a file source, we can copy directly
            log.debug("Copying file '%s' to '%s'", src_path, dst_path)
            dst_path.write_bytes(src_path.read_bytes())
        else:
            # src_path not set, it's an http URL, try to download
            log.debug("Downloading URL '%s' to '%s'", url, dst_path)
            if not retries and config.is_set('OCRD_DOWNLOAD_RETRIES'):
                retries = config.OCRD_DOWNLOAD_RETRIES
            if timeout is None and config.is_set('OCRD_DOWNLOAD_TIMEOUT'):
                timeout = config.OCRD_DOWNLOAD_TIMEOUT
            session = requests.Session()
            retries = Retry(total=retries or 0,
                            status_forcelist=[
                                # probably too wide (only transient failures):
                                408, # Request Timeout
                                409, # Conflict
                                412, # Precondition Failed
                                417, # Expectation Failed
                                423, # Locked
                                424, # Fail
                                425, # Too Early
                                426, # Upgrade Required
                                428, # Precondition Required
                                429, # Too Many Requests
                                440, # Login Timeout
                                500, # Internal Server Error
                                503, # Service Unavailable
                                504, # Gateway Timeout
                                509, # Bandwidth Limit Exceeded
                                529, # Site Overloaded
                                598, # Proxy Read Timeout
                                599, # Proxy Connect Timeout
                    ])
            adapter = HTTPAdapter(max_retries=retries)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            contents = handle_oai_response(response)
            dst_path.write_bytes(contents)

        return str(ret)

    def workspace_from_url(
        self,
        mets_url,
        dst_dir=None,
        clobber_mets=False,
        mets_basename=None,
        download=False,
        src_baseurl=None,
        mets_server_url=None,
        **kwargs
    ):
        """
        Create a workspace from a METS by URL (i.e. clone if :py:attr:`mets_url` is remote or :py:attr:`dst_dir` is given).

        Arguments:
            mets_url (string): Source METS URL or filesystem path
        Keyword Arguments:
            dst_dir (string, None): Target directory for the workspace. \
                By default create a temporary directory under :py:data:`ocrd.constants.TMP_PREFIX`. \
                (The resulting path can be retrieved via :py:attr:`ocrd.Workspace.directory`.)
            clobber_mets (boolean, False): Whether to overwrite existing ``mets.xml``. \
                By default existing ``mets.xml`` will raise an exception.
            download (boolean, False): Whether to also download all the files referenced by the METS
            src_baseurl (string, None): Base URL for resolving relative file locations
            mets_server_url (string, None): URI of TCP or local path of UDS for METS server handling
                the `OcrdMets` of the workspace. By default the METS will be read from and written to
                the filesystem directly.
            **kwargs (): Passed on to ``OcrdMets.find_files`` if download == True

        Download (clone) :py:attr:`mets_url` to ``mets.xml`` in :py:attr:`dst_dir`, unless 
        the former is already local and the latter is ``none`` or already identical to its directory name.

        Returns:
            a new :py:class:`~ocrd.workspace.Workspace`
        """
        log = getLogger('ocrd.resolver.workspace_from_url')

        if mets_url is None:
            raise ValueError("Must pass 'mets_url' workspace_from_url")

        # if mets_url is a relative filename, make it absolute
        if is_local_filename(mets_url) and not Path(mets_url).is_absolute():
            mets_url = str(Path(Path.cwd() / mets_url))

        # if mets_basename is not given, use the last URL segment of the mets_url
        if mets_basename is None:
            mets_basename = nth_url_segment(mets_url, -1)

        # If src_baseurl wasn't given, determine from mets_url by removing last url segment
        if not src_baseurl:
            last_segment = nth_url_segment(mets_url)
            src_baseurl = remove_non_path_from_url(remove_non_path_from_url(mets_url)[:-len(last_segment)])

        # resolve dst_dir
        if not dst_dir:
            if is_local_filename(mets_url):
                log.debug("Deriving dst_dir %s from %s", Path(mets_url).parent, mets_url)
                dst_dir = Path(mets_url).parent
            else:
                log.debug("Creating ephemeral workspace '%s' for METS @ <%s>", dst_dir, mets_url)
                dst_dir = mkdtemp(prefix=TMP_PREFIX)
        # XXX Path.resolve is always strict in Python <= 3.5, so create dst_dir unless it exists consistently
        if not Path(dst_dir).exists():
            Path(dst_dir).mkdir(parents=True, exist_ok=False)
        dst_dir = str(Path(dst_dir).resolve())

        log.debug("workspace_from_url\nmets_basename='%s'\nmets_url='%s'\nsrc_baseurl='%s'\ndst_dir='%s'",
            mets_basename, mets_url, src_baseurl, dst_dir)
        self.download_to_directory(dst_dir, mets_url, basename=mets_basename, if_exists='overwrite' if clobber_mets else 'skip')

        workspace = Workspace(self, dst_dir, mets_basename=mets_basename, baseurl=src_baseurl, mets_server_url=mets_server_url)

        if download:
            for f in workspace.mets.find_files(**kwargs):
                workspace.download_file(f)

        return workspace

    def workspace_from_nothing(self, directory, mets_basename=DEFAULT_METS_BASENAME, clobber_mets=False):
        """
        Create an empty workspace.

        Arguments:
            directory (string): Target directory for the workspace. \
                If ``none``, create a temporary directory under :py:data:`ocrd.constants.TMP_PREFIX`. \
                (The resulting path can be retrieved via :py:attr:`ocrd.Workspace.directory`.)
        Keyword Arguments:
            clobber_mets (boolean, False): Whether to overwrite existing ``mets.xml``. \
                By default existing ``mets.xml`` will raise an exception.

        Returns:
            a new :py:class:`~ocrd.workspace.Workspace`
        """
        log = getLogger('ocrd.resolver.workspace_from_nothing')
        if directory is None:
            directory = mkdtemp(prefix=TMP_PREFIX)
        Path(directory).mkdir(parents=True, exist_ok=True)
        mets_path = Path(directory, mets_basename)
        if mets_path.exists() and not clobber_mets:
            raise FileExistsError("METS '%s' already exists in '%s' and clobber_mets not set." % (mets_basename, directory))
        mets = OcrdMets.empty_mets()
        log.info("Writing METS to %s", mets_path)
        mets_path.write_bytes(mets.to_xml(xmllint=True))

        return Workspace(self, directory, mets, mets_basename=mets_basename)

    def resolve_mets_arguments(self, directory, mets_url, mets_basename=DEFAULT_METS_BASENAME, mets_server_url=None):
        """
        Resolve the ``--mets``, ``--mets-basename``, `--directory``,
        ``--mets-server-url``, arguments into a coherent set of arguments
        according to https://github.com/OCR-D/core/issues/517
        """
        log = getLogger('ocrd.resolver.resolve_mets_arguments')

        mets_is_remote = mets_url and (mets_url.startswith('http://') or mets_url.startswith('https://'))

        # XXX we might want to be more strict like this but it might break # legacy code
        # Allow --mets and --directory together iff --mets is a remote URL
        # if directory and mets_url and not mets_is_remote:
        #     raise ValueError("Use either --mets or --directory, not both")

        # If --mets is a URL, a directory must be explicitly provided (not strictly necessary, but retained for legacy behavior)
        if not directory and mets_is_remote:
            raise ValueError("--mets is an http(s) URL but no --directory was given")

        # Determine --mets-basename
        if not mets_basename and mets_url:
            mets_basename = Path(mets_url).name
        elif not mets_basename and not mets_url:
            mets_basename = DEFAULT_METS_BASENAME
        elif mets_basename and mets_url:
            raise ValueError("Use either --mets or --mets-basename, not both")
        else:
            warn("--mets-basename is deprecated. Use --mets/--directory instead", DeprecationWarning)

        # Determine --directory and --mets-url
        if not directory and not mets_url:
            directory = Path.cwd()
            mets_url = Path(directory, mets_basename)
        elif directory and not mets_url:
            directory = Path(directory).resolve()
            mets_url = directory / mets_basename
        elif not directory and mets_url:
            mets_url = Path(mets_url).resolve()
            directory = mets_url.parent
        else: # == directory and mets_url:
            directory = Path(directory).resolve()
            if not mets_is_remote:
                # --mets is just a basename and --directory is set, so treat --mets as --mets-basename
                if Path(mets_url).parent == Path('.'):
                    mets_url = directory / mets_url
                else:
                    mets_url = Path(mets_url).resolve()
                    if not is_file_in_directory(directory, mets_url):
                        raise ValueError("--mets '%s' has a directory part inconsistent with --directory '%s'" % (mets_url, directory))

        return str(Path(directory).resolve()), str(mets_url), str(mets_basename), mets_server_url


