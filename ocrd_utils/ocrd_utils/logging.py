"""
Logging setup

By default: Log with lastResort logger, usually STDERR.

Logging can be overridden either programmatically in code using the library or by creating one or more of

- /etc/ocrd_logging.py
- $HOME/ocrd_logging.py
- $PWD/ocrd_logging.py

These files will be executed in the context of ocrd/ocrd_logging.py, with `logging` global set.
"""
# pylint: disable=no-member

from __future__ import absolute_import

import logging
import os

__all__ = [
    'logging',
    'getLogger',
    'getLevelName',
    'setOverrideLogLevel'
]

_overrideLogLevel = None

_ocrdLevel2pythonLevel = {
    'TRACE':    'DEBUG',
    'OFF':      'CRITICAL',
    'FATAL':    'ERROR',
}

def getLevelName(lvl):
    """
    Get (numerical) python logging level for (string) spec-defined log level name.
    """
    lvl = _ocrdLevel2pythonLevel.get(lvl, lvl)
    return logging.getLevelName(lvl)

def setOverrideLogLevel(lvl):
    """
    Override all logger filter levels to include lvl and above.


    - Set root logger level
    - iterates all existing loggers and sets their log level to ``NOTSET``.

    Args:
        lvl (string): Log level name.
    """
    if lvl is None:
        return
    logging.info('Overriding log level globally to %s', lvl)
    lvl = getLevelName(lvl)
    _overrideLogLevel = lvl # lgtm [py/unused-local-variable]
    logging.getLogger('').setLevel(lvl)
    for loggerName in logging.Logger.manager.loggerDict:
        logger = logging.Logger.manager.loggerDict[loggerName]
        if isinstance(logger, logging.PlaceHolder):
            continue
        logger.setLevel(logging.NOTSET)

def getLogger(*args, **kwargs):
    logger = logging.getLogger(*args, **kwargs)
    if _overrideLogLevel is not None:
        logger.setLevel(logging.NOTSET)
    return logger

# Default logging config

def initLogging():
    """
    Sets logging defaults
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(message)s',
        datefmt='%H:%M:%S')
    logging.getLogger('').setLevel(logging.INFO)
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

initLogging()
