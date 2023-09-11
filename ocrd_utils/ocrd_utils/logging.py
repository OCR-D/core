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
    Wrapper around ``logging.getLogger`` that alls :py:func:`initLogging` if
    that wasn't explicitly called before.
    """
    if not _initialized_flag:
        initLogging()
    logger = logging.getLogger(*args, **kwargs)
    return logger

def setOverrideLogLevel(lvl, silent=False):
    """
    Override the output log level of the handlers attached to the ``ocrd`` logger.

    Args:
        lvl (string): Log level name.
        silent (boolean): Whether to log the override call
    """
    if not _initialized_flag:
        initLogging()
    ocrd_logger = logging.getLogger('ocrd')

    if lvl is None:
        if not silent:
            ocrd_logger.info('Reset log level override')
        ocrd_logger.setLevel(logging.NOTSET)
    else:
        if not silent:
            ocrd_logger.info('Overriding log level globally to %s', lvl)
        ocrd_logger.setLevel(lvl)

def initLogging(builtin_only=False, basic_config=True, force_reinit=False):
    """
    Reset ``ocrd`` logger, read logging configuration if exists, otherwise use basicConfig

    initLogging is to be called by OCR-D/core once, i.e.
        -  for the ``ocrd`` CLI
        -  for the processor wrapper methods

    Other processes that use OCR-D/core as a library can, but do not have to, use this functionality.

    Keyword Args:
        - basic_config (bool, False): Whether to attach the handler to the
                                      root logger instead of just the ``ocrd`` logger
                                      like ``logging.basicConfig`` does.
        - builtin_only (bool, False): Whether to search for logging configuration
                                      on-disk (``False``) or only use the
                                      hard-coded config (``True``). For testing
        - force_reinit (bool, False): Whether to ignore the module-level
                                      ``_initialized_flag``. For testing only.
    """
    global _initialized_flag
    if _initialized_flag and not force_reinit:
        return

    # https://docs.python.org/3/library/logging.html#logging.disable
    # If logging.disable(logging.NOTSET) is called, it effectively removes this
    # overriding level, so that logging output again depends on the effective
    # levels of individual loggers.
    logging.disable(logging.NOTSET)

    # remove all handlers for the ocrd logger
    for handler in logging.getLogger('ocrd').handlers[:]:
        logging.getLogger('ocrd').removeHandler(handler)

    config_file = None
    if not builtin_only:
        CONFIG_PATHS = [
            Path.cwd(),
            Path.home(),
            Path('/etc'),
        ]
        config_file = next((f for f \
                in [p / 'ocrd_logging.conf' for p in CONFIG_PATHS] \
                if f.exists()),
                None)
    if config_file:
        logging.config.fileConfig(config_file)
        logging.getLogger('ocrd.logging').debug("Picked up logging config at %s", config_file)
    else:
        # Default logging config
        ocrd_handler = logging.StreamHandler(stream=sys.stderr)
        ocrd_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIMEFMT))
        if basic_config:
            logging.getLogger('').addHandler(ocrd_handler)
        else:
            logging.getLogger('ocrd').addHandler(ocrd_handler)
        logging.getLogger('ocrd').setLevel('INFO')
        #  logging.getLogger('ocrd.resolver').setLevel(logging.INFO)
        #  logging.getLogger('ocrd.resolver.download_to_directory').setLevel(logging.INFO)
        #  logging.getLogger('ocrd.resolver.add_files_to_mets').setLevel(logging.INFO)
        logging.getLogger('PIL').setLevel(logging.INFO)
        # To cut back on the `Self-intersection at or near point` INFO messages
        logging.getLogger('shapely.geos').setLevel(logging.ERROR)
        logging.getLogger('tensorflow').setLevel(logging.ERROR)

    _initialized_flag = True

def disableLogging():
    """
    Disables all logging of the ``ocrd`` logger and descendants
    """
    global _initialized_flag # pylint: disable=global-statement
    if _initialized_flag:
        logging.getLogger('ocrd.logging').debug("Disabling logging")
    _initialized_flag = False
    # logging.basicConfig(level=logging.CRITICAL)
    # logging.disable(logging.ERROR)
    # remove all handlers for the ocrd logger
    for handler in logging.getLogger('ocrd').handlers[:]:
        logging.getLogger('ocrd').removeHandler(handler)

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
