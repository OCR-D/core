from click.testing import CliRunner

from src.ocrd_network.constants import AgentType, JobState
from tests.base import assets
from tests.network.config import test_config
from ocrd_network.cli.client import client_cli

PROCESSING_SERVER_URL = test_config.PROCESSING_SERVER_URL


def test_client_processing_processor():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    runner = CliRunner()
    result = runner.invoke(
        client_cli,
        args=[
            "processing", "processor", "ocrd-dummy",
            "--address", PROCESSING_SERVER_URL,
            "--mets", path_to_mets,
            "--input-file-grp", "OCR-D-IMG",
            "--output-file-grp", "OCR-D-DUMMY-TEST-CLIENT",
            "--agent-type", AgentType.PROCESSING_WORKER
        ]
    )
    # TODO: Do a better result check
    assert result.output.count("finished") == 1


def test_client_processing_workflow():
    pass

