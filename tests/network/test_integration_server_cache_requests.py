from typing import List
from src.ocrd_network.constants import AgentType
from src.ocrd_network.models import PYJobInput
from src.ocrd_network.server_cache import CacheProcessingRequests


def test_has_workspace_cached_requests():
    workspace_key = "/path/to/mets.xml"
    processing_request1 = PYJobInput(
        path_to_mets=workspace_key,
        input_file_grps=List["DEFAULT"],
        output_file_grps=List["OCR-D-BIN"],
        agent_type=AgentType.PROCESSING_WORKER,
        page_id="PHYS_0001..PHYS_0003",
        parameters={}
    )
    requests_cache = CacheProcessingRequests()
    assert not requests_cache.has_workspace_cached_requests(workspace_key=workspace_key)
    requests_cache.cache_request(workspace_key=workspace_key, data=processing_request1)
    assert requests_cache.has_workspace_cached_requests(workspace_key=workspace_key)
