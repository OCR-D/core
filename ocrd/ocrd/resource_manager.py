from pathlib import Path

from yaml import safe_load

from .constants import RESOURCE_LIST_FILENAME

from ocrd_validators import OcrdResourceListValidator
from ocrd_utils import getLogger
from ocrd_utils.constants import HOME
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
        if executable:
            resources = [(executable, self.database[executable])]
        else:
            resources = [(x, y) for x, y in self.database.items()]
        return resources

    def list_installed(self, executable=None):
        ret = []
        for executable in [executable] if executable else self.database.keys():
            reslist = []
            for res_filename in list_all_resources(executable):
                res_name = Path(res_filename).name
                resdict = [x for x in self.database[executable] if x['name'] == res_name]
                if not resdict:
                    resdict = [{'name': res_name, 'url': '???', 'description': '???', 'version_range': '???'}]
                reslist.append(resdict[0])
            ret.append((executable, reslist))
        return ret
