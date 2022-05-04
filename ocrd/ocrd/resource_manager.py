from pathlib import Path
from os.path import join
from os import environ, listdir, getcwd, path
from shutil import copytree
from datetime import datetime
from tarfile import open as open_tarfile
from urllib.parse import urlparse, unquote

import requests
from yaml import safe_load, safe_dump

from ocrd_validators import OcrdResourceListValidator
from ocrd_utils import getLogger
from ocrd_utils.os import get_processor_resource_types, list_all_resources, pushd_popd
from .constants import RESOURCE_LIST_FILENAME, RESOURCE_USER_LIST_COMMENT

class OcrdResourceManager():

    """
    Managing processor resources
    """
    def __init__(self, userdir=None, xdg_config_home=None, xdg_data_home=None):
        self.log = getLogger('ocrd.resource_manager')
        self.database = {}

        self._xdg_data_home = xdg_data_home
        self._xdg_config_home = xdg_config_home
        self._userdir = userdir
        self.user_list = Path(self.xdg_config_home, 'ocrd', 'resources.yml')

        self.load_resource_list(Path(RESOURCE_LIST_FILENAME))
        if not self.user_list.exists():
            if not self.user_list.parent.exists():
                self.user_list.parent.mkdir(parents=True)
            with open(str(self.user_list), 'w', encoding='utf-8') as f:
                f.write(RESOURCE_USER_LIST_COMMENT)
        self.load_resource_list(self.user_list)

    @property
    def userdir(self):
        if not self._userdir:
            self._userdir = path.expanduser('~')
            if 'HOME' in environ and environ['HOME'] != path.expanduser('~'):
                self._userdir = environ['HOME']
        return self._userdir

    @property
    def xdg_data_home(self):
        if not self._xdg_data_home:
            if 'XDG_DATA_HOME' in environ:
                self._xdg_data_home = environ['XDG_DATA_HOME']
            else:
                self._xdg_data_home = join(self.userdir, '.local', 'share')
        return self._xdg_data_home

    @property
    def xdg_config_home(self):
        if not self._xdg_config_home:
            if 'XDG_CONFIG_HOME' in environ:
                self._xdg_config_home = environ['XDG_CONFIG_HOME']
            else:
                self._xdg_config_home = join(self.userdir, '.config')
        return self._xdg_config_home

    def load_resource_list(self, list_filename, database=None):
        if not database:
            database = self.database
        if list_filename.is_file():
            with open(list_filename, 'r', encoding='utf-8') as f:
                list_loaded = safe_load(f) or {}
            report = OcrdResourceListValidator.validate(list_loaded)
            if not report.is_valid:
                self.log.error('\n'.join(report.errors))
                raise ValueError("Resource list %s is invalid!" % (list_filename))
            for executable, resource_list in list_loaded.items():
                if executable not in database:
                    database[executable] = []
                # Prepend, so user provided is sorted before builtin
                database[executable] = list_loaded[executable] + database[executable]
        return database

    def list_available(self, executable=None):
        """
        List models available for download by processor
        """
        if executable:
            return [(executable, self.database[executable])]
        return self.database.items()

    def list_installed(self, executable=None):
        """
        List installed resources, matching with registry by ``name``
        """
        ret = []
        if executable:
            all_executables = [executable]
        else:
            # resources we know about
            all_executables = list(self.database.keys())
            # resources in the file system
            parent_dirs = [join(x, 'ocrd-resources') for x in [self.xdg_data_home, '/usr/local/share']]
            for parent_dir in parent_dirs:
                if Path(parent_dir).exists():
                    all_executables += [x for x in listdir(parent_dir) if x.startswith('ocrd-')]
        for this_executable in set(all_executables):
            reslist = []
            has_dirs, has_files = get_processor_resource_types(this_executable)
            for res_filename in list_all_resources(this_executable):
                if Path(res_filename).is_dir() and not has_dirs:
                    continue
                if Path(res_filename).is_file() and not has_files:
                    continue
                res_name = Path(res_filename).name
                resdict = [x for x in self.database.get(this_executable, []) if x['name'] == res_name]
                if not resdict:
                    self.log.info("%s resource '%s' (%s) not a known resource, creating stub in %s'", this_executable, res_name, res_filename, self.user_list)
                    resdict = [self.add_to_user_database(this_executable, res_filename)]
                resdict[0]['path'] = res_filename
                reslist.append(resdict[0])
            ret.append((this_executable, reslist))
        return ret

    def add_to_user_database(self, executable, res_filename, url=None):
        """
        Add a stub entry to the user resource.yml
        """
        res_name = Path(res_filename).name
        res_size = Path(res_filename).stat().st_size
        with open(self.user_list, 'r', encoding='utf-8') as f:
            user_database = safe_load(f) or {}
        if executable not in user_database:
            user_database[executable] = []
        resources_found = self.find_resources(executable=executable, name=res_name, database=user_database)
        if not resources_found:
            resdict = {
                'name': res_name,
                'url': url if url else '???',
                'description': 'Found at %s on %s' % (self.resource_dir_to_location(res_filename), datetime.now()),
                'version_range': '???',
                'size': res_size
            }
            user_database[executable].append(resdict)
        else:
            resdict = resources_found[0]
        with open(self.user_list, 'w', encoding='utf-8') as f:
            f.write(RESOURCE_USER_LIST_COMMENT)
            f.write('\n')
            f.write(safe_dump(user_database))
        self.load_resource_list(self.user_list)
        return resdict

    def find_resources(self, executable=None, name=None, url=None, database=None):
        """
        Find resources in the registry
        """
        if not database:
            database = self.database
        ret = []
        if executable and executable not in database.keys():
            return ret
        for executable in [executable] if executable else database.keys():
            for resdict in database[executable]:
                if not name and not url:
                    ret.append((executable, resdict))
                elif url and url == resdict['url']:
                    ret.append((executable, resdict))
                elif name and name == resdict['name']:
                    ret.append((executable, resdict))
        return ret

    @property
    def default_resource_dir(self):
        return self.location_to_resource_dir('data')

    def location_to_resource_dir(self, location):
        return '/usr/local/share/ocrd-resources' if location == 'system' else \
                join(self.xdg_data_home, 'ocrd-resources') if location == 'data' else \
                getcwd()

    def resource_dir_to_location(self, resource_path):
        resource_path = str(resource_path)
        return 'system' if resource_path.startswith('/usr/local/share/ocrd-resources') else \
               'data' if resource_path.startswith(join(self.xdg_data_home, 'ocrd-resources')) else \
               'cwd' if resource_path.startswith(getcwd()) else \
               resource_path

    def parameter_usage(self, name, usage='as-is'):
        if usage == 'as-is':
            return name
        elif usage == 'without-extension':
            return Path(name).stem
        raise ValueError("No such usage '%s'" % usage)

    def _download_impl(self, url, filename, progress_cb=None, size=None):
        log = getLogger('ocrd.resource_manager._download_impl')
        log.info("Downloading %s to %s" % (url, filename))
        with open(filename, 'wb') as f:
            with requests.get(url, stream=True) as r:
                total = size if size else int(r.headers.get('content-length'))
                for data in r.iter_content(chunk_size=4096):
                    if progress_cb:
                        progress_cb(len(data))
                    f.write(data)

    def _copy_impl(self, src_filename, filename, progress_cb=None):
        log = getLogger('ocrd.resource_manager._copy_impl')
        log.info("Copying %s" % src_filename)
        with open(filename, 'wb') as f_out, open(src_filename, 'rb') as f_in:
            while True:
                chunk = f_in.read(4096)
                if chunk:
                    f_out.write(chunk)
                    if progress_cb:
                        progress_cb(len(chunk))
                else:
                    break

    # TODO Proper caching (make head request for size, If-Modified etc)
    def download(
        self,
        executable,
        url,
        basedir,
        overwrite=False,
        no_subdir=False,
        name=None,
        resource_type='file',
        path_in_archive='.',
        progress_cb=None,
        size=None,
    ):
        """
        Download a resource by URL
        """
        log = getLogger('ocrd.resource_manager.download')
        destdir = Path(basedir) if no_subdir else Path(basedir, executable)
        if not name:
            url_parsed = urlparse(url)
            name = Path(unquote(url_parsed.path)).name
        fpath = Path(destdir, name)
        is_url = url.startswith('https://') or url.startswith('http://')
        if fpath.exists() and not overwrite:
            log.info("%s to be %s to %s which already exists and overwrite is False" % (url, 'downloaded' if is_url else 'copied', fpath))
            return fpath
        destdir.mkdir(parents=True, exist_ok=True)
        if resource_type == 'file':
            if is_url:
                self._download_impl(url, fpath, progress_cb)
            else:
                self._copy_impl(url, fpath, progress_cb)
        elif resource_type == 'tarball':
            with pushd_popd(tempdir=True) as tempdir:
                if is_url:
                    self._download_impl(url, 'download.tar.xx', progress_cb, size)
                else:
                    self._copy_impl(url, 'download.tar.xx', progress_cb)
                Path('out').mkdir()
                with pushd_popd('out'):
                    log.info("Extracting tarball to %s/out" % tempdir)
                    with open_tarfile('../download.tar.xx', 'r:*') as tar:
                        tar.extractall()
                    log.info("Copying '%s' from extracted tarball %s/out to %s" % (path_in_archive, tempdir, fpath))
                    copytree(path_in_archive, str(fpath))
        # TODO
        # elif resource_type == 'github-dir':
        return fpath
