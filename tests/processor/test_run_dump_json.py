from pytest import main
from tests.data.wf_testcase import TestCase, SAMPLE_NAME_TOO_VERBOSE

from ocrd.processor.helpers import run_dump_json

class TestProcessorHelperRunDumpJson(TestCase):

    def test_540(self):
        """
        https://github.com/OCR-D/core/issues/540
        https://github.com/OCR-D/core/issues/589
        """
        ocrd_tool = run_dump_json(SAMPLE_NAME_TOO_VERBOSE)
        print(ocrd_tool)
        assert ocrd_tool['executable'] == SAMPLE_NAME_TOO_VERBOSE

if __name__ == '__main__': main([__file__])
