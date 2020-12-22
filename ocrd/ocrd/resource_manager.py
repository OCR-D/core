from pathlib import Path
import re
from shutil import copyfileobj

import requests
from yaml import safe_load

from .constants import RESOURCE_LIST_FILENAME

from ocrd_validators import OcrdResourceListValidator
from ocrd_utils import getLogger
from ocrd_utils.constants import HOME, XDG_CACHE_HOME
from ocrd_utils.os import list_resource_candidates, list_all_resources

builtin_list_filename = Path(RESOURCE_LIST_FILENAME)
user_list_filename = Path(HOME, 'ocrd', 'resources.yml')

class OcrdResourceManager():

    """
    Managing processor resources
    """
    def __init__(self):
        self.log = getLogger('ocrd.resource_manager')
        self.database = {}
        self.load_resource_list(builtin_list_filename)
        self.load_resource_list(user_list_filename)

    def load_resource_list(self, list_filename):
        if list_filename.is_file():
            with open(list_filename, 'r', encoding='utf-8') as f:
                list_loaded = safe_load(f)
            report = OcrdResourceListValidator.validate(list_loaded)
            if not report.is_valid:
                self.log.error('\n'.join(report.errors))
                raise ValueError("Resource list %s is invalid!" % (list_filename))
            for executable, resource_list in list_loaded.items():
                if executable not in self.database:
                    self.database[executable] = []
                # Prepend, so user provided is sorted before builtin
                self.database[executable] = list_loaded[executable] + self.database[executable]

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
        for executable in [executable] if executable else self.database.keys():
            reslist = []
            for res_filename in list_all_resources(executable):
                res_name = Path(res_filename).name
                resdict = [x for x in self.database[executable] if x['name'] == res_name]
                if not resdict:
                    # TODO handle gracefully
                    resdict = [{'name': res_name, 'url': '???', 'description': '???', 'version_range': '???'}]
                reslist.append(resdict[0])
            ret.append((executable, reslist))
        return ret

    def find_resources(self, executable=None, name=None, url=None):
        """
        Find resources in the registry
        """
        ret = []
        if executable and executable not in self.database.keys():
            return ret
        for executable in [executable] if executable else self.database.keys():
            for resdict in self.database[executable]:
                if url and url == resdict['url']:
                    ret.append((executable, resdict))
                elif name and name == resdict['name']:
                    ret.append((executable, resdict))
        return ret

    def parameter_usage(self, name, usage='as-is'):
        if usage == 'as-is':
            return name
        if usage == 'without-extension':
            return Path(name).stem

    # TODO Proper caching (make head request for size, If-Modified etc)
    def download(self, executable, url, overwrite=False, basedir=XDG_CACHE_HOME, name=None, resource_type='file', path_in_archive='.'):
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
            with requests.get(url, stream=True) as r:
                with open(fpath, 'wb') as f:
                    copyfileobj(r.raw, f)
        # elif resource_type == archive:
        # TODO
        # elif resource_type == 'archive':
        # elif resource_type == 'github-dir':
        # elif resource_type == 'github-file':
