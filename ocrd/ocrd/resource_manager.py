from pathlib import Path
from os.path import join
from os import environ, listdir
import re
from shutil import copytree
from datetime import datetime
from tarfile import open as open_tarfile

import requests
from yaml import safe_load, safe_dump

from ocrd_validators import OcrdResourceListValidator
from ocrd_utils import getLogger
from ocrd_utils.constants import HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME
from ocrd_utils.os import list_all_resources, pushd_popd

from .constants import RESOURCE_LIST_FILENAME, RESOURCE_USER_LIST_COMMENT

class OcrdResourceManager():

    """
    Managing processor resources
    """
    def __init__(self):
        self.log = getLogger('ocrd.resource_manager')
        self.database = {}
        self.load_resource_list(Path(RESOURCE_LIST_FILENAME))
        self.user_list = Path(XDG_CONFIG_HOME, 'ocrd', 'resources.yml')
        if not self.user_list.exists():
            if not self.user_list.parent.exists():
                self.user_list.parent.mkdir()
            with open(str(self.user_list), 'w', encoding='utf-8') as f:
                f.write(RESOURCE_USER_LIST_COMMENT)
        self.load_resource_list(self.user_list)

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
        return [(x, y) for x, y in self.database.items()]

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
            parent_dirs = [XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME]
            if 'VIRTUAL_ENV' in environ:
                parent_dirs += [join(environ['VIRTUAL_ENV'], 'share')]
            for parent_dir in parent_dirs:
                all_executables += [x for x in listdir(parent_dir) if x.startswith('ocrd-')]
        for this_executable in set(all_executables):
            reslist = []
            for res_filename in list_all_resources(this_executable):
                res_name = Path(res_filename).name
                resdict = [x for x in self.database.get(this_executable, []) if x['name'] == res_name]
                if not resdict:
                    self.log.info("%s resource '%s' (%s) not a known resource, creating stub in %s'" % (this_executable, res_name, res_filename, self.user_list))
                    resdict = [self.add_to_user_database(this_executable, res_filename)]
                reslist.append(resdict[0])
            ret.append((this_executable, reslist))
        return ret

    def add_to_user_database(self, executable, res_filename):
        """
        Add a stub entry to the user resource.yml
        """
        res_name = Path(res_filename).name
        res_size = Path(res_filename).stat().st_size
        with open(self.user_list, 'r', encoding='utf-8') as f:
            user_database = safe_load(f) or {}
        if executable not in user_database:
            user_database[executable] = []
        if not self.find_resources(executable=executable, name=res_name, database=user_database):
            resdict = {
                'name': res_name,
                'url': '???',
                'description': 'Found at %s on %s' % (res_filename, datetime.now()),
                'version_range': '???',
                'size': res_size
            }
            user_database[executable].append(resdict)
        with open(self.user_list, 'w', encoding='utf-8') as f:
            f.write(RESOURCE_USER_LIST_COMMENT)
            f.write('\n')
            f.write(safe_dump(user_database))
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

    def parameter_usage(self, name, usage='as-is'):
        if usage == 'as-is':
            return name
        if usage == 'without-extension':
            return Path(name).stem

    def _download_impl(self, url, filename, progress_cb=None):
        with open(filename, 'wb') as f:
            with requests.get(url, stream=True) as r:
                total = int(r.headers.get('content-length'))
                # copyfileobj(r.raw, f_write_tar)
                for data in r.iter_content(chunk_size=4096):
                    if progress_cb:
                        progress_cb(len(data))
                    f.write(data)

    # TODO Proper caching (make head request for size, If-Modified etc)
    def download(
        self,
        executable,
        url,
        overwrite=False,
        basedir=XDG_CACHE_HOME,
        name=None,
        resource_type='file',
        path_in_archive='.',
        progress_cb=None,
    ):
        """
        Download a resource by URL
        """
        log = getLogger('ocrd.resource_manager.download')
        destdir = Path(basedir, executable)
        if not name:
            name = re.sub('[^A-Za-z0-9]', '', url)
        fpath = Path(destdir, name)
        if fpath.exists() and not overwrite:
            log.info("%s to be downloaded to %s which already exists and overwrite is False" % (url, fpath))
            return fpath
        destdir.mkdir(parents=True, exist_ok=True)
        if resource_type == 'file':
            self._download_impl(url, fpath, progress_cb)
        elif resource_type == 'tarball':
            with pushd_popd(tempdir=True):
                log.info("Downloading %s" % url)
                self._download_impl(url, 'download.tar.xx', progress_cb)
                Path('out').mkdir()
                with pushd_popd('out'):
                    log.info("Extracting tarball")
                    with open_tarfile('../download.tar.xx', 'r:*') as tar:
                        tar.extractall()
                    log.info("Copying '%s' from tarball to %s" % (path_in_archive, fpath))
                    copytree(path_in_archive, str(fpath))
        # TODO
        # elif resource_type == 'github-dir':
        return fpath
