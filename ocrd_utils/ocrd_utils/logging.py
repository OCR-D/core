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
import logging.config
import os

from .constants import LOG_FORMAT, LOG_TIMEFMT

__all__ = [
    'logging',
    'getLogger',
    'getLevelName',
    'initLogging',
    'setOverrideLogLevel'
]

_overrideLogLevel = None

_ocrdLevel2pythonLevel = {
    'TRACE': 'DEBUG',
    'OFF': 'CRITICAL',
    'FATAL': 'ERROR',
}

class PropagationShyLogger(logging.Logger):

    def addHandler(self, hdlr):
        super().addHandler(hdlr)
        self.propagate = not self.handlers

    def removeHandler(self, hdlr):
        super().removeHandler(hdlr)
        self.propagate = not self.handlers

logging.setLoggerClass(PropagationShyLogger)
logging.getLogger().propagate = False

def getLevelName(lvl):
    """
    Get (string) python logging level for (string) spec-defined log level name.
    """
    lvl = _ocrdLevel2pythonLevel.get(lvl, lvl)
    return logging.getLevelName(lvl)

def setOverrideLogLevel(lvl, silent=False):
    """
    Override all logger filter levels to include lvl and above.


    - Set root logger level
    - iterates all existing loggers and sets their log level to ``NOTSET``.

    Args:
        lvl (string): Log level name.
        silent (boolean): Whether to log the override call
    """
    if lvl is None:
        return
    if not silent:
        logging.info('Overriding log level globally to %s', lvl)
    lvl = getLevelName(lvl)
    global _overrideLogLevel # pylint: disable=global-statement
    _overrideLogLevel = lvl
    logging.getLogger('').setLevel(lvl)
    for loggerName in logging.Logger.manager.loggerDict:
        logger = logging.Logger.manager.loggerDict[loggerName]
        if isinstance(logger, logging.PlaceHolder):
            continue
        logger.setLevel(logging.NOTSET)

def getLogger(*args, **kwargs):
    """
    Wrapper around ``logging.getLogger`` that respects `overrideLogLevel <#setOverrideLogLevel>`_.
    """
    logger = logging.getLogger(*args, **kwargs)
    if _overrideLogLevel is not None:
        logger.setLevel(logging.NOTSET)
    return logger

# Default logging config

def initLogging():
    """
    Reset root logger, read logging configuration if exists, otherwise use basicConfig
    """

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    global _overrideLogLevel # pylint: disable=global-statement
    _overrideLogLevel = None

    CONFIG_PATHS = [
        os.path.curdir,
        os.path.join(os.path.expanduser('~')),
        '/etc',
    ]
    for p in CONFIG_PATHS:
        config_file = os.path.join(p, 'ocrd_logging.conf')
        if os.path.exists(config_file):
            logging.config.fileConfig(config_file)
            return

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_TIMEFMT)
    logging.getLogger('').setLevel(logging.INFO)
    #  logging.getLogger('ocrd.resolver').setLevel(logging.INFO)
    #  logging.getLogger('ocrd.resolver.download_to_directory').setLevel(logging.INFO)
    #  logging.getLogger('ocrd.resolver.add_files_to_mets').setLevel(logging.INFO)
    logging.getLogger('PIL').setLevel(logging.INFO)
    # To cut back on the `Self-intersection at or near point` INFO messages
    logging.getLogger('shapely.geos').setLevel(logging.ERROR)


initLogging()
