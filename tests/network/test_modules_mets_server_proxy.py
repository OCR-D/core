from os.path import abspath, dirname, exists, join
from pathlib import Path
from pytest import fixture
from shutil import rmtree, copytree
from src.ocrd.mets_server import OcrdAgentModel, OcrdFileModel
from src.ocrd_network.tcp_to_uds_mets_proxy import MetsServerProxy
from src.ocrd_network.runtime_data import Deployer
from tests.base import assets

PS_CONFIG_PATH = str(join(abspath(dirname(__file__)), "ps_config.yml"))
WORKSPACE_ASSET_PATH = "SBB0000F29300010000/data"
WORKSPACE_UNIQUE_IDENTIFIER = "http://resolver.staatsbibliothek-berlin.de/SBB0000F29300010000"
TEST_WORKSPACE_DIR = "/tmp/ocrd-mets-server-proxy"


@fixture(scope="function", name="start_uds_mets_server")
def fixture_start_uds_mets_server() -> Path:
    if exists(TEST_WORKSPACE_DIR):
        rmtree(TEST_WORKSPACE_DIR, ignore_errors=True)
    copytree(assets.path_to(WORKSPACE_ASSET_PATH), TEST_WORKSPACE_DIR)

    deployer = Deployer(config_path=PS_CONFIG_PATH)
    mets_server_url = deployer.start_uds_mets_server(ws_dir_path=TEST_WORKSPACE_DIR)
    yield mets_server_url
    rmtree(TEST_WORKSPACE_DIR, ignore_errors=True)


def test_get_request_unique_identifier(start_uds_mets_server):
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "GET",
        "response_type": "text",
        "request_url": "unique_identifier",
        "request_data": {}
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    assert response_dict["text"] == WORKSPACE_UNIQUE_IDENTIFIER


def test_get_request_workspace_path(start_uds_mets_server):
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "GET",
        "response_type": "text",
        "request_url": "workspace_path",
        "request_data": {}
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    assert response_dict["text"] == TEST_WORKSPACE_DIR


def test_get_request_file_groups(start_uds_mets_server):
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "GET",
        "response_type": "dict",
        "request_url": "file_groups",
        "request_data": {}
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    # print(response.__dict__)
    file_groups = response_dict["file_groups"]
    assert len(file_groups) == 17


def test_post_request_agent(start_uds_mets_server):
    test_agent_name = "Module test agent"
    test_agent_type = "Tester type"
    test_agent_othertype = "Other tester type"
    test_agent_role = "Test role"
    test_agent_otherrole = "Other tester role"
    ocrd_agent_model = OcrdAgentModel.create(
        name=test_agent_name,
        _type=test_agent_type,
        role=test_agent_role,
        otherrole=test_agent_otherrole,
        othertype=test_agent_othertype,
        notes=[]
    )
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "POST",
        "response_type": "class",
        "request_url": "agent",
        "request_data": {
            "class": ocrd_agent_model.dict()
         }
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    assert response_dict["name"] == test_agent_name
    assert response_dict["type"] == test_agent_type
    assert response_dict["role"] == test_agent_role
    assert response_dict["otherrole"] == test_agent_otherrole
    assert response_dict["othertype"] == test_agent_othertype


def test_post_request_reload(start_uds_mets_server):
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "POST",
        "response_type": "text",
        "request_url": "reload",
        "request_data": {}
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    # print(response.__dict__)
    assert response_dict["text"] == f'Reloaded from {TEST_WORKSPACE_DIR}'


def test_post_request_file(start_uds_mets_server):
    test_file_id = "File test id"
    test_file_group = "OCR-D-IMG"
    test_page_id = "PHYS_5555"
    test_mimetype = "Test mimetype"
    test_url = "Test url"
    test_local_filename = "Test local filename"
    ocrd_file_model = OcrdFileModel.create(
        file_id=test_file_id,
        file_grp=test_file_group,
        page_id=test_page_id,
        mimetype=test_mimetype,
        url=test_url,
        local_filename=test_local_filename
    )
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "POST",
        "response_type": "class",
        "request_url": "file",
        "request_data": {
            "class": ocrd_file_model.dict()
        }
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    # TODO: assert new file was successfully added


def test_get_request_files(start_uds_mets_server):
    test_file_group = "OCR-D-IMG"
    test_non_existing_file_group = "FOO-D-FOO"
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "GET",
        "response_type": "class",
        "request_url": "file",
        "request_data": {
            "params": {
                "file_grp": test_file_group
            }
        }
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    assert len(response_dict["files"]) == 3, "Expected to find exatly 3 matching files"
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "GET",
        "response_type": "class",
        "request_url": "file",
        "request_data": {
            "params": {
                "file_grp": test_non_existing_file_group
            }
        }
    }
    response_dict = MetsServerProxy().forward_tcp_request(request_body=request_body)
    assert len(response_dict["files"]) == 0, "Expected to find no matching files but found some"
