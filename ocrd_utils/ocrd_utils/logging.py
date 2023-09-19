"""
Logging setup

By default: Log with lastResort logger, usually STDERR.

Logging can be overridden either programmatically in code using the library or by creating one or more of

- /etc/ocrd_logging.py
- $HOME/ocrd_logging.py
- $PWD/ocrd_logging.py

These files will be executed in the context of ocrd/ocrd_logging.py, with `logging` global set.

Changes as of 2023-08-20:

    - Try to be less intrusive with OCR-D specific logging conventions to
      make it easier and less surprising to define logging behavior when
      using OCR-D/core as a library
    - Change setOverrideLogLevel to only override the log level of the ``ocrd``
      logger and its descendants
    - initLogging will set exactly one handler, for the root logger or for the
      ``ocrd`` logger.
    - Child loggers should propagate to the ancestor logging (default
      behavior of the logging library - no more PropagationShyLogger)
    - disableLogging only removes any handlers from the ``ocrd`` logger
"""
# pylint: disable=no-member

from __future__ import absolute_import

from traceback import format_stack

import logging
import logging.config
from pathlib import Path
import sys
from warnings import warn

from .constants import LOG_FORMAT, LOG_TIMEFMT
from .config import config

ROOT_OCRD_LOGGER_NAME = 'ocrd'

__all__ = [
    'disableLogging',
    'getLevelName',
    'getLogger',
    'initLogging',
    'logging',
    'setOverrideLogLevel',
]

LOGGING_DEFAULTS = {
    'ocrd': logging.INFO,
    'ocrd_network': logging.DEBUG,
    # 'ocrd.resolver': logging.INFO,
    # 'ocrd.resolver.download_to_directory': logging.INFO,
    # 'ocrd.resolver.add_files_to_mets': logging.INFO,
    # To cut back on the `Self-intersection at or near point` INFO messages
    'shapely.geos': logging.ERROR,
    'tensorflow': logging.ERROR,
    'PIL': logging.INFO,
    'paramiko.transport': logging.INFO
}

# Holds the levels of all loggers before initLogging was called
# to be reset on disableLogging
# LOGGING_LEVELS_BEFORE_INIT = {}

_initialized_flag = False

_ocrdLevel2pythonLevel = {
    'TRACE': 'DEBUG',
    'OFF': 'CRITICAL',
    'FATAL': 'ERROR',
}

def tf_disable_interactive_logs():
    try:
        from os import environ
        # This env variable must be set before importing from Keras
        environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        from tensorflow.keras.utils import disable_interactive_logging
        # Enabled interactive logging throws an exception
        # due to a call of sys.stdout.flush()
        disable_interactive_logging()
    except ImportError:
        # Nothing should be handled here if TF is not available
        pass

def getLevelName(lvl):
    """
    Get (string) python logging level for (string) spec-defined log level name.
    """
    lvl = _ocrdLevel2pythonLevel.get(lvl, lvl)
    return logging.getLevelName(lvl)

def getLogger(*args, **kwargs):
    """
    Delegates to ``logging.getLogger``. Retained for backwards-compatibility.
    """
    logger = logging.getLogger(*args, **kwargs)
    return logger

def setOverrideLogLevel(lvl, silent=not config.OCRD_LOGGING_DEBUG):
    """
    Override the output log level of the handlers attached to the ``ocrd`` logger.

    Args:
        lvl (string): Log level name.
        silent (boolean): Whether to log the override call
    """
    if not _initialized_flag:
        initLogging(silent=silent)
    ocrd_logger = logging.getLogger(ROOT_OCRD_LOGGER_NAME)

    if lvl is None:
        if not silent:
            print('[LOGGING] Reset log level override', file=sys.stderr)
        ocrd_logger.setLevel(logging.NOTSET)
    else:
        if not silent:
            print(f'[LOGGING] Overriding ocrd log level to {lvl}', file=sys.stderr)
        ocrd_logger.setLevel(lvl)

def initLogging(builtin_only=False, config_file_only=False, force_reinit=False, silent=not config.OCRD_LOGGING_DEBUG):
    """
    Reset ``ocrd`` logger, read logging configuration if exists, otherwise use basicConfig

    initLogging is to be called by OCR-D/core once, i.e.
        -  for the ``ocrd`` CLI
        -  for the processor wrapper methods

    Other processes that use OCR-D/core as a library can, but do not have to, use this functionality.

    Keyword Args:
        - builtin_only (bool, False): Whether to search for logging configuration
                                      on-disk (``False``) or only use the
                                      hard-coded config (``True``). For testing
        - config_file_only (bool, False): Only try to load from ocrd_logging.conf,
                                          raise a ValueError if no config file found
        - force_reinit (bool, False): Whether to ignore the module-level
                                      ``_initialized_flag``. For testing only.
        - silent (bool, True): Whether to log logging behavior by printing to stderr
    """
    global _initialized_flag
    if not silent:
        print(
            '[LOGGING] initLogging initialized=%s root.handlers=%s ocrd.handlers = %s' % (
            _initialized_flag,
            logging.root.handlers,
            logging.getLogger(ROOT_OCRD_LOGGER_NAME).handlers),
            file=sys.stderr)
    if _initialized_flag and not force_reinit:
        return

    # # save level of existing loggers, in case there was some initial
    # # configuration before initLogging
    # for logger_name, logger in logging.root.manager.loggerDict.items():
    #     if not isinstance(logger, logging.Logger):
    #         continue
    #     LOGGING_LEVELS_BEFORE_INIT[logger_name] = logger.getEffectiveLevel()
    # print(LOGGING_LEVELS_BEFORE_INIT)
    # assert 0

    # Reset the logging, remove handlers and logging overrides
    # disableLogging(silent=silent)

    config_file = None
    if not builtin_only:
        CONFIG_PATHS = [
            Path.cwd(),
            Path.home(),
            Path('/etc'),
        ]
        config_file = [f for f \
                in [p / 'ocrd_logging.conf' for p in CONFIG_PATHS] \
                if f.exists()]
    if config_file:
        if len(config_file) > 1 and not silent:
            print(f"[LOGGING] Multiple logging configuration files found at {config_file}", file=sys.stderr)
        config_file = config_file[0]
    if not config_file and config_file_only:
        raise ValueError("logging.initLogging received config_file_only=True but no config file was found")
    if config_file and not builtin_only:
        logging.config.fileConfig(config_file)
        if not silent:
            print("[LOGGING] Picked up logging config at %s", config_file, file=sys.stderr)
        _initialized_flag = True
        return

    # Default logging config
    if not silent:
        print("[LOGGING] Initializing logging with built-in defaults", file=sys.stderr)
    ocrd_handler = logging.StreamHandler(stream=sys.stderr)
    ocrd_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
    ocrd_handler.setLevel(logging.NOTSET)
    logging.getLogger(ROOT_OCRD_LOGGER_NAME).addHandler(ocrd_handler)
    for logger_name, logger_level in LOGGING_DEFAULTS.items():
        logging.getLogger(logger_name).setLevel(logger_level)
    _initialized_flag = True

def disableLogging(silent=not config.OCRD_LOGGING_DEBUG):
    """
    Disables all logging of the ``ocrd`` logger and descendants

    Keyword Args:
        - silent (bool, True): Whether to log logging behavior by printing to stderr
    """
    global _initialized_flag # pylint: disable=global-statement
    if _initialized_flag and not silent:
        print("[LOGGING] Disabling logging", file=sys.stderr)

    # https://docs.python.org/3/library/logging.html#logging.disable
    # If logging.disable(logging.NOTSET) is called, it effectively removes this
    # overriding level, so that logging output again depends on the effective
    # levels of individual loggers.
    logging.disable(logging.NOTSET)

    # remove all handlers from all the loggers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # # Restore pre-initLogging defaults
    # for logger_name, lvl in LOGGING_LEVELS_BEFORE_INIT.items():
    #     logging.getLogger(logger_name).setLevel(lvl)

    # Reset our defaults
    for logger_name in LOGGING_DEFAULTS:
        logging.getLogger(logger_name).setLevel(logging.NOTSET)

    _initialized_flag = False

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
