import logging

from unittest import mock
from pytest import fixture
from shutil import copy
# from logging import StreamHandler, Formatter
from os.path import join, dirname, curdir, abspath
import os

from tests.base import main, FIFOIO

from ocrd.resolver import Resolver
from ocrd_models.utils import extract_mets_from_oai_content
from ocrd_utils import getLogger, initLogging, LOG_FORMAT, disableLogging


@fixture(name="response_dir")
def fixture_response_dir(tmpdir):
    tmp_response = tmpdir.mkdir('responses')
    yield tmp_response


@fixture(name="workspace_dir")
def _fixture_workspace_dir(response_dir):
    src3 = 'ocrd_utils/ocrd_logging.conf'
    copy(src3, str(response_dir.join('ocrd_logging.conf')))
    src = './tests/data/response/oai_get_record_2200909.xml'
    target_file = str(response_dir.join('oai_get_record_2200909.xml'))
    copy(src, target_file)
    old_dir = os.path.abspath(curdir)
    os.chdir(response_dir)
    yield response_dir
    os.chdir(old_dir)


@fixture(name="oai_response_content")
def fixture_oai_2200909_content(workspace_dir):
    data_path = join(workspace_dir, 'oai_get_record_2200909.xml')
    with open(data_path, 'rb') as f:
        return f.read()


@fixture(name="plain_xml_response_content")
def fixture_xml_kant_content(response_dir):
    src2 = './tests/data/response/mets_kant_aufklaerung_1784.xml'
    target_file2 = str(response_dir.join('mets_kant_aufklaerung_1784.xml'))
    copy(src2, target_file2)
    data_path = join(response_dir, 'mets_kant_aufklaerung_1784.xml')
    with open(data_path, 'rb') as f:
        return f.read()


def test_extract_mets_from_oai_content(oai_response_content):
    """Ensure that OAI-prelude gets dropped"""

    result = extract_mets_from_oai_content(oai_response_content)
    expected_start = b'<?xml version="1.0" encoding="UTF-8"?>\r\n<mets:mets'
    assert result.startswith(expected_start)
    assert b'OAI-PHM' not in result


def test_handle_response_mets(plain_xml_response_content):
    """Ensure plain XML/Text Response is not broken"""

    result = extract_mets_from_oai_content(plain_xml_response_content)
    expected_start = b'<?xml version="1.0"'
    assert result.startswith(expected_start)


@mock.patch("requests.get")
def test_handle_common_oai_response(mock_get, response_dir, oai_response_content):
    """Base use case with valid OAI Response data"""
    # initLogging()

    # arrange
    url = 'http://digital.bibliothek.uni-halle.de/hd/oai/?verb=GetRecord&metadataPrefix=mets&mode=xml&identifier=9049'
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = oai_response_content
    headers = {'Content-Type': 'text/xml'}
    mock_get.return_value.headers = headers
    resolver = Resolver()

    # act
    result = resolver.download_to_directory(response_dir, url)

    # assert
    mock_get.assert_called_once_with(url)
    assert result == 'oai'
    # disableLogging()


@mock.patch("requests.get")
def test_handle_response_for_invalid_content(mock_get, workspace_dir, caplog):
    """If invalid content is returned, store warning log entry"""

    # arrange
    url = 'http://digital.bibliothek.uni-halle.de/hd/oai/?verb=GetRecord&metadataPrefix=mets&mode=xml&identifier=foo'
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'foo bar'
    headers = {'Content-Type': 'text/plain'}
    mock_get.return_value.headers = headers
    resolver = Resolver()
    initLogging(config_paths=[workspace_dir])

    # capture log
    log = logging.getLogger('ocrd_models.utils.handle_oai_response')
    # log = getLogger('ocrd_models.utils.handle_oai_response')
    capt = FIFOIO(256)
    sh = logging.StreamHandler(capt)
    sh.setFormatter(logging.Formatter(LOG_FORMAT))
    log.setLevel('WARNING')

    # old_dir = os.path.abspath(curdir)
    # os.chdir(response_dir)
    # 
    print(f"################### CUR_DIR {abspath(curdir)}")
    print(f'################### files: {",".join(os.listdir(curdir))}')
    resolver.download_to_directory(workspace_dir, url)

    # assert
    mock_get.assert_called_once_with(url)
    # log_output = capt.getvalue()
    # assert log_output
    # assert capt.getvalue()
    assert caplog.records
    # log_record = caplog.records[0]
    # assert log_record.levelname == 'CRITICAL'
    #assert log_record.name == 'ocrd_models.utils.handle_oai_response'
    # assert log_record.name == 'root'
    # assert "textual response but no xml: b'foo bar'" in log_record.message
    # assert "textual response but no xml: b'foo bar'" in log_output
    # os.chdir(old_dir)


if __name__ == '__main__':
    main(__file__)
