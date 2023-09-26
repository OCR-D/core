from unittest.mock import patch
from pytest import fixture
from shutil import copy
from logging import StreamHandler, Formatter
from os.path import join, dirname

from requests import Session
from tests.base import main, FIFOIO

from ocrd.resolver import Resolver
from ocrd_models.utils import extract_mets_from_oai_content
from ocrd_utils import getLogger, initLogging, LOG_FORMAT


@fixture(name="response_dir")
def fixture_response_dir(tmpdir):
    src = './tests/data/response/oai_get_record_2200909.xml'
    target_file = str(tmpdir.mkdir('responses').join(
        'oai_get_record_2200909.xml'))
    copy(src, target_file)
    src2 = './tests/data/response/mets_kant_aufklaerung_1784.xml'
    target_file2 = str(tmpdir.join('responses').join(
        'mets_kant_aufklaerung_1784.xml'))
    copy(src2, target_file2)
    return dirname(target_file)


@fixture(name="oai_response_content")
def fixture_oai_2200909_content(response_dir):
    data_path = join(response_dir, 'oai_get_record_2200909.xml')
    with open(data_path, 'rb') as f:
        return f.read()


@fixture(name="plain_xml_response_content")
def fixture_xml_kant_content(response_dir):
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


@patch.object(Session, "get")
def test_handle_common_oai_response(mock_get, response_dir, oai_response_content):
    """Base use case with valid OAI Response data"""
    initLogging()

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
    mock_get.assert_called_once_with(url, timeout=None)
    assert result == 'oai'


@patch.object(Session, "get")
def test_handle_response_for_invalid_content(mock_get, response_dir):
    """If invalid content is returned, store warning log entry"""

    # arrange
    url = 'http://digital.bibliothek.uni-halle.de/hd/oai/?verb=GetRecord&metadataPrefix=mets&mode=xml&identifier=foo'
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'foo bar'
    headers = {'Content-Type': 'text/plain'}
    mock_get.return_value.headers = headers
    resolver = Resolver()
    initLogging()

    # capture log
    log = getLogger('ocrd.models.utils.handle_oai_response')
    capt = FIFOIO(256)
    sh = StreamHandler(capt)
    sh.setFormatter(Formatter(LOG_FORMAT))
    log.addHandler(sh)

    # act
    resolver.download_to_directory(response_dir, url)

    # assert
    mock_get.assert_called_once_with(url, timeout=None)
    log_output = capt.getvalue()
    assert 'WARNING ocrd.models.utils.handle_oai_response' in log_output


if __name__ == '__main__':
    main(__file__)
