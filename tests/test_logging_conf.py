# -*- coding: utf-8 -*-
"""Specification Logging Configuration"""

import os
import pathlib
import re
import shutil
import sys

from ocrd_utils.logging import (
    initLogging,
    getLogger
)

import pytest

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../ocrd')
TEST_ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent


@pytest.fixture(name="logging_conf")
def _fixture_loggin_conf(tmpdir):

    path_logging_conf_orig = os.path.join(
        TEST_ROOT, 'ocrd_utils', 'ocrd_logging.conf')
    path_logging_conf_dest = os.path.join(tmpdir, 'ocrd_logging.conf')
    shutil.copy(path_logging_conf_orig, path_logging_conf_dest)
    return str(tmpdir)


def test_cli_log_level_set(logging_conf, capsys):
    """Ensure example ocrd_logging.conf is valid and produces desired record format"""

    # arrange
    os.chdir(logging_conf)
    initLogging()
    test_logger = getLogger('')

    # act
    test_logger.info("test logger initialized")

    log_info_output = capsys.readouterr().out
    must_not_match = r"^\d{4}-\d{2}-\d{2}.*"
    assert not re.match(must_not_match, log_info_output)
    match_pattern = r"^\d{2}:\d{2}:\d{2}.*"
    assert re.match(match_pattern, log_info_output)
