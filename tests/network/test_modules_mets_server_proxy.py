from os.path import abspath, dirname, exists, join
from shutil import rmtree, copytree
from src.ocrd.mets_server import OcrdAgentModel
from src.ocrd_network.tcp_to_uds_mets_proxy import MetsServerProxy
from src.ocrd_network.runtime_data import Deployer
from tests.base import assets

PS_CONFIG_PATH = str(join(abspath(dirname(__file__)), "ps_config.yml"))
WORKSPACE_ASSET_PATH = "SBB0000F29300010000/data"
TEST_WORKSPACE_DIR = "/tmp/ocrd-mets-server-proxy"


def test_get_request():
    if exists(TEST_WORKSPACE_DIR):
        rmtree(TEST_WORKSPACE_DIR, ignore_errors=True)
    copytree(assets.path_to(WORKSPACE_ASSET_PATH), TEST_WORKSPACE_DIR)

    deployer = Deployer(config_path=PS_CONFIG_PATH)
    deployer.start_uds_mets_server(ws_dir_path=TEST_WORKSPACE_DIR)

    mets_server_proxy = MetsServerProxy()
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "GET",
        "request_url": "unique_identifier",
        "request_data": {}
    }
    response = mets_server_proxy.forward_tcp_request(request_body=request_body)
    # print(response.__dict__)
    assert response.status_code == 200
    assert response.text == "http://resolver.staatsbibliothek-berlin.de/SBB0000F29300010000"


def test_post_request_with_data():
    if exists(TEST_WORKSPACE_DIR):
        rmtree(TEST_WORKSPACE_DIR, ignore_errors=True)
    copytree(assets.path_to(WORKSPACE_ASSET_PATH), TEST_WORKSPACE_DIR)

    deployer = Deployer(config_path=PS_CONFIG_PATH)
    deployer.start_uds_mets_server(ws_dir_path=TEST_WORKSPACE_DIR)

    test_agent_name = "Module Test Agent"
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

    mets_server_proxy = MetsServerProxy()
    request_body = {
        "workspace_path": TEST_WORKSPACE_DIR,
        "method_type": "POST",
        "request_url": "agent",
        "request_data": ocrd_agent_model.dict()
    }
    response = mets_server_proxy.forward_tcp_request(request_body=request_body)
    # print(response.__dict__)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == test_agent_name
    assert response_json["type"] == test_agent_type
    assert response_json["role"] == test_agent_role
    assert response_json["otherrole"] == test_agent_otherrole
    assert response_json["othertype"] == test_agent_othertype
