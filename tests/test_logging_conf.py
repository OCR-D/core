# -*- coding: utf-8 -*-
"""Specification Logging Configuration"""

import os
import pathlib
import re
import shutil
import sys

from ocrd_utils import pushd_popd
from ocrd_utils.logging import (
    initLogging,
    getLogger,
    disableLogging,
)

import pytest

from tests.base import main

# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../ocrd')
TEST_ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent

def resetLogging():
    disableLogging()
    initLogging()


@pytest.fixture(name="logging_conf")
def _fixture_logging_conf(tmpdir):

    path_logging_conf_orig = os.path.join(
        str(TEST_ROOT), 'src', 'ocrd_utils', 'ocrd_logging.conf')
    path_logging_conf_dest = os.path.join(str(tmpdir), 'ocrd_logging.conf')
    shutil.copy(path_logging_conf_orig, path_logging_conf_dest)
    return str(tmpdir)


def test_configured_dateformat(logging_conf, capsys):
    """Ensure example ocrd_logging.conf is valid and produces desired record format"""

    # arrange
    with pushd_popd(logging_conf):
        resetLogging()
        test_logger = getLogger('')

        # act
        test_logger.info("test logger initialized")

        log_info_output = capsys.readouterr().err
        must_not_match = r"^\d{4}-\d{2}-\d{2}.*"
        assert not re.match(must_not_match, log_info_output)
        match_pattern = r"^\d{2}:\d{2}:\d{2}.*"
        assert re.match(match_pattern, log_info_output)


def test_configured_tensorflow_logger_present(logging_conf, capsys):
    """Ensure example ocrd_logging.conf is valid and contains logger tensorflow"""

    # arrange
    os.chdir(logging_conf)
    resetLogging()
    logger_under_test = getLogger('tensorflow')

    # act info
    logger_under_test.info("tensorflow logger initialized")
    log_info_output = capsys.readouterr().err
    assert not log_info_output

    # act error
    logger_under_test.error("tensorflow has error")
    log_error_output = capsys.readouterr().err
    assert log_error_output


def test_configured_shapely_logger_present(logging_conf, capsys):
    """Ensure example ocrd_logging.conf is valid and contains logger shapely.geos"""

    # arrange
    os.chdir(logging_conf)
    resetLogging()
    logger_under_test = getLogger('shapely.geos')

    # act info
    logger_under_test.info("shapely.geos logger initialized")
    log_info_output = capsys.readouterr().err
    assert not log_info_output

    # act error
    logger_under_test.error("shapely alert")
    log_error_output = capsys.readouterr().err
    assert log_error_output

if __name__ == '__main__':
    main(__file__)
