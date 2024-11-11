"""
Logging setup

By default: Log with lastResort logger, usually STDERR.

Logging can be overridden either programmatically in code using the library or by creating one or more of

- ``/etc/ocrd_logging.py``
- ``$HOME/ocrd_logging.py``
- ``$PWD/ocrd_logging.py``

These files will be executed in the context of ocrd/ocrd_logging.py, with `logging` global set.

Changes as of 2023-08-20:

    - Try to be less intrusive with OCR-D specific logging conventions to
      make it easier and less surprising to define logging behavior when
      using OCR-D/core as a library
    - Change :py:meth:`setOverrideLogLevel` to only override the log level of the ``ocrd``
      logger and its descendants
    - :py:meth:`initLogging` will set exactly one handler, for the root logger or for the
      ``ocrd`` logger.
    - Child loggers should propagate to the ancestor logging (default
      behavior of the logging library - no more ``PropagationShyLogger``)
    - :py:meth:`disableLogging` only removes any handlers from the ``ocrd`` logger
"""
# pylint: disable=no-member

from __future__ import absolute_import

import logging
import logging.config
from pathlib import Path
import sys

from .constants import LOG_FORMAT, LOG_TIMEFMT
from .config import config


__all__ = [
    'disableLogging',
    'getLevelName',
    'getLogger',
    'initLogging',
    'logging',
    'setOverrideLogLevel',
]

LOGGING_DEFAULTS = {
    '': logging.WARNING,
    'ocrd': logging.INFO,
    'ocrd_network': logging.INFO,
    # 'ocrd.resolver': logging.INFO,
    # 'ocrd.resolver.download_to_directory': logging.INFO,
    # 'ocrd.resolver.add_files_to_mets': logging.INFO,
    # To cut back on the `Self-intersection at or near point` INFO messages
    'shapely.geos': logging.ERROR,
    'tensorflow': logging.ERROR,
    'PIL': logging.INFO,
    'paramiko.transport': logging.INFO,
    'uvicorn.access': logging.DEBUG,
    'uvicorn.error': logging.DEBUG,
    'uvicorn': logging.INFO,
    'multipart': logging.INFO,
}

_initialized_flag = False

_ocrdLevel2pythonLevel = {
    'TRACE': 'DEBUG',
    'OFF': 'CRITICAL',
    'FATAL': 'ERROR',
}

def tf_disable_interactive_logs():
    try:
        from os import environ # pylint: disable=import-outside-toplevel
        # This env variable must be set before importing from Keras
        environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        from tensorflow.keras.utils import disable_interactive_logging # pylint: disable=import-outside-toplevel
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
    Wrapper around ``logging.getLogger`` that calls :py:func:`initLogging` if
    that wasn't explicitly called before.
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
    if lvl is not None:
        lvl = getLevelName(lvl)
        if not _initialized_flag:
            initLogging(silent=silent)
        # affect all configured loggers
        for logger_name in logging.root.manager.loggerDict:
            if not silent:
                print(f'[LOGGING] Overriding {logger_name} log level to {lvl}', file=sys.stderr)
            logging.getLogger(logger_name).setLevel(lvl)

def get_logging_config_files():
    """
    Return a list of all ``ocrd_logging.conf`` files found in CWD, HOME or /etc.
    """
    CONFIG_PATHS = [
        Path.cwd(),
        Path.home(),
        Path('/etc'),
    ]
    return [f for f \
            in [p / 'ocrd_logging.conf' for p in CONFIG_PATHS] \
            if f.exists()]

def initLogging(builtin_only=False, force_reinit=False, silent=not config.OCRD_LOGGING_DEBUG):
    """
    Reset ``ocrd`` logger, read logging configuration if exists, otherwise use :py:meth:`logging.basicConfig`

    This is to be called by OCR-D/core only once, i.e.
        -  for the ``ocrd`` CLI
        -  for the processor wrapper methods

    Other processes that use OCR-D/core as a library can, but do not have to, use this functionality.

    Keyword Args:
        - builtin_only (bool): Whether to search for logging configuration
              on-disk (``False``) or only use the hard-coded config (``True``).
              For testing
        - force_reinit (bool): Whether to ignore the module-level ``_initialized_flag``.
              For testing only
        - silent (bool): Whether to log logging behavior by printing to stderr
    """
    global _initialized_flag
    if _initialized_flag:
        if force_reinit:
            disableLogging(silent=silent)
        else:
            return

    config_file = None
    if not builtin_only:
        config_file = get_logging_config_files()
    if config_file:
        if len(config_file) > 1 and not silent:
            print(f"[LOGGING] Multiple logging configuration files found at {config_file}, using first one", file=sys.stderr)
        config_file = config_file[0]
        if not silent:
            print(f"[LOGGING] Picked up logging config at {config_file}", file=sys.stderr)
        logging.config.fileConfig(config_file)
    else:
        if not silent:
            print("[LOGGING] Initializing logging with built-in defaults", file=sys.stderr)
        # Default logging config
        ocrd_handler = logging.StreamHandler(stream=sys.stderr)
        ocrd_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
        ocrd_handler.setLevel(logging.DEBUG)
        root_logger = logging.getLogger('')
        root_logger.addHandler(ocrd_handler)
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
    _initialized_flag = False
    # remove all handlers we might have added (via initLogging on builtin or file config)
    for logger_name in logging.root.manager.loggerDict:
        if not silent:
            print(f'[LOGGING] Resetting {logger_name} log level and handlers')
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.NOTSET)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Python default log level is WARNING
    logging.root.setLevel(logging.WARNING)

