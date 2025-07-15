from pytest import fixture
from src.ocrd_network.constants import AgentType
from src.ocrd_network.models import PYJobInput


@fixture(scope="session", name="processing_request_1")
def fixture_processing_request_1() -> PYJobInput:
    workspace_key = "/path/to/mets.xml"
    processing_request1 = PYJobInput(
        path_to_mets=workspace_key,
        input_file_grps=["DEFAULT"],
        output_file_grps=["OCR-D-BIN"],
        agent_type=AgentType.PROCESSING_WORKER,
        page_id="PHYS_0001..PHYS_0003",
        parameters={}
    )
    yield processing_request1
