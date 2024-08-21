
from functools import lru_cache
from json import JSONDecodeError, loads
from pathlib import Path
from subprocess import run, PIPE

from ocrd_utils.introspect import resource_string
from ocrd_utils.logging import getLogger

#from .ocrd_tool_validator import OcrdToolValidator


@lru_cache()
def get_ocrd_tool_json(executable):
    """
    Get the ``ocrd-tool`` description of ``executable``.
    """
    ocrd_tool = {}
    executable_name = Path(executable).name
    try:
        ocrd_all_tool = loads(resource_string('ocrd', 'ocrd-all-tool.json'))
        ocrd_tool = ocrd_all_tool[executable]
    except (JSONDecodeError, OSError, KeyError):
        try:
            ocrd_tool = loads(run([executable, '--dump-json'], stdout=PIPE).stdout)
        except (JSONDecodeError, OSError) as e:
            getLogger('ocrd.utils.get_ocrd_tool_json').error(f'{executable} --dump-json produced invalid JSON: {e}')
    if 'resource_locations' not in ocrd_tool:
        ocrd_tool['resource_locations'] = ['data', 'cwd', 'system', 'module']
    # OcrdToolValidator.validate(ocrd_tool)
    return ocrd_tool

