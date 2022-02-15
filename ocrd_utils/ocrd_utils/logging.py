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
from traceback import format_stack

import logging
import logging.config
import os
import sys

from .constants import LOG_FORMAT, LOG_TIMEFMT

__all__ = [
    'disableLogging',
    'getLevelName',
    'getLogger',
    'initLogging',
    'logging',
    'setOverrideLogLevel',
]

_initialized_flag = False
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
    root_logger = logging.getLogger('')
    if not silent:
        root_logger.info('Overriding log level globally to %s', lvl)
    lvl = getLevelName(lvl)
    global _overrideLogLevel # pylint: disable=global-statement
    _overrideLogLevel = lvl
    for loggerName in logging.Logger.manager.loggerDict:
        logger = logging.Logger.manager.loggerDict[loggerName]
        if isinstance(logger, logging.PlaceHolder):
            continue
        logger.setLevel(logging.NOTSET)
    root_logger.setLevel(lvl)

def getLogger(*args, **kwargs):
    """
    Wrapper around ``logging.getLogger`` that respects `overrideLogLevel <#setOverrideLogLevel>`_.
    """
    if not _initialized_flag:
        initLogging()
        logging.getLogger('').critical('getLogger was called before initLogging. Source of the call:')
        for line in [x for x in format_stack(limit=2)[0].split('\n') if x]:
            logging.getLogger('').critical(line)
    name = args[0]
    logger = logging.getLogger(*args, **kwargs)
    if _overrideLogLevel and name:
        logger.setLevel(logging.NOTSET)
    return logger

def initLogging():
    """
    Reset root logger, read logging configuration if exists, otherwise use basicConfig
    """
    global _initialized_flag # pylint: disable=global-statement
    if _initialized_flag:
        logging.getLogger('').critical('initLogging was called multiple times. Source of latest call:')
        for line in [x for x in format_stack(limit=2)[0].split('\n') if x]:
            logging.getLogger('').critical(line)

    logging.disable(logging.NOTSET)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    CONFIG_PATHS = [
        os.path.curdir,
        os.path.join(os.path.expanduser('~')),
        '/etc',
    ]
    config_file = next((f for f \
            in [os.path.join(p, 'ocrd_logging.conf') for p in CONFIG_PATHS] \
            if os.path.exists(f)),
            None)
    if config_file:
        logging.config.fileConfig(config_file)
        logging.getLogger('ocrd.logging').debug("Picked up logging config at %s" % config_file)
    else:
        # Default logging config
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_TIMEFMT, stream=sys.stderr)
        logging.getLogger('').setLevel(logging.INFO)
        #  logging.getLogger('ocrd.resolver').setLevel(logging.INFO)
        #  logging.getLogger('ocrd.resolver.download_to_directory').setLevel(logging.INFO)
        #  logging.getLogger('ocrd.resolver.add_files_to_mets').setLevel(logging.INFO)
        logging.getLogger('PIL').setLevel(logging.INFO)
        # To cut back on the `Self-intersection at or near point` INFO messages
        logging.getLogger('shapely.geos').setLevel(logging.ERROR)
        logging.getLogger('tensorflow').setLevel(logging.ERROR)

    if _overrideLogLevel:
        # for existing loggers that won't have getLogger do this
        # (because they were instantiated through logging.getLogger
        #  instead of ours, or come from logging.config.fileConfig),
        # unset log levels so the global override can apply:
        for loggerName in logging.Logger.manager.loggerDict:
            logger = logging.Logger.manager.loggerDict[loggerName]
            if isinstance(logger, logging.PlaceHolder):
                continue
            logger.setLevel(logging.NOTSET)
        logging.getLogger('').setLevel(_overrideLogLevel)

    _initialized_flag = True

def disableLogging():
    global _initialized_flag # pylint: disable=global-statement
    _initialized_flag = False
    global _overrideLogLevel # pylint: disable=global-statement
    _overrideLogLevel = None
    logging.basicConfig(level=logging.CRITICAL)
    logging.disable(logging.ERROR)

# Initializing stream handlers at module level
# would cause message output in all runtime contexts,
# including those which are already run for std output
# (--dump-json, --version, ocrd-tool, bashlib etc).
# So this needs to be an opt-in from the CLIs/decorators:
#initLogging()
# Also, we even have to block log output for libraries
# (like matplotlib/tensorflow) which set up logging
# themselves already:
disableLogging()
