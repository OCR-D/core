import re
from click.testing import CliRunner
import pytest
from ocrd_network.cli.client import workflow_cli


runner = CliRunner()

def test_check_workflow_tasks_argument():
    """
    https://github.com/OCR-D/core/pull/1358
    """
    with pytest.raises(ValueError, match=re.escape("Either -w/--path-to-workflow option or task argument(s) is required, but neither was provided.")):
        runner.invoke(workflow_cli, [
            'run',
            '--address', 'https://irrelevant',
            '--path-to-mets', 'irrelevant',
        ], catch_exceptions=False)
    with pytest.raises(ValueError, match=re.escape("Either -w/--path-to-workflow option or task argument(s) is required, not both.")):
        runner.invoke(workflow_cli, [
            'run',
            '--address', 'https://irrelevant',
            '--path-to-mets', 'irrelevant',
            '--path-to-workflow', 'irrelevant',
            'task1', 'task2'
        ], catch_exceptions=False)
