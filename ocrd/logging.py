"""
Logging setup

By default: Log with lastResort logger, usually STDERR.

Logging can be overridden either programmatically in code using the library or by creating one or more of

- /etc/ocrd_logging.py
- $HOME/ocrd_logging.py
- $PWD/ocrd_logging.py

These files will be executed in the context of ocrd/ocrd_logging.py, with `logging` global set.
"""
from __future__ import absolute_import

import logging
import os

__all__ = ['logging', 'getLogger']

def getLogger(*args, **kwargs):
    return logging.getLogger(*args, **kwargs)

# Default logging config

logging.basicConfig(level=logging.DEBUG)
#  logging.getLogger('ocrd.resolver').setLevel(logging.INFO)
#  logging.getLogger('ocrd.resolver.download_to_directory').setLevel(logging.INFO)
#  logging.getLogger('ocrd.resolver.add_files_to_mets').setLevel(logging.INFO)
logging.getLogger('PIL').setLevel(logging.INFO)

# Allow overriding

CONFIG_PATHS = [
    os.path.curdir,
    os.path.join(os.path.expanduser('~')),
    '/etc',
]


for p in CONFIG_PATHS:
    config_file = os.path.join(p, 'ocrd_logging.py')
    if os.path.exists(config_file):
        logging.info("Loading logging configuration from '%s'", config_file)
        with open(config_file) as f:
            code = compile(f.read(), config_file, 'exec')
            exec(code, globals(), locals()) # pylint: disable=exec-used
