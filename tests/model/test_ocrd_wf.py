from tests.base import main
from tests.data.wf_testcase import (
    TestCase,

    SAMPLE_NAME_REQUIRED_PARAM,
    PARAM_JSON,
)

from ocrd_models.constants import OCRD_WF_SHEBANG
from ocrd_models import OcrdWf

class TestOcrdWf(TestCase):

    def test_parse_minimal(self):
        wf = OcrdWf.parse(OCRD_WF_SHEBANG)
        self.assertEqual(wf.steps, [])
        self.assertEqual(wf.assignments, {})

    def test_parse_assignment(self):
        wf = OcrdWf.parse(OCRD_WF_SHEBANG + "\nfoo=bar")
        self.assertEqual(wf.steps, [])
        self.assertEqual(wf.assignments, {'foo': 'bar'})

    def test_parse_comments(self):
        wf = OcrdWf.parse(OCRD_WF_SHEBANG + "\n# foo\n     # bar")
        self.assertEqual(wf.steps, [])
        self.assertEqual(wf.assignments, {})

    def test_parse_steps_and_assignments(self):
        wf = OcrdWf.parse(OCRD_WF_SHEBANG + "\n" + \
                "ocrd-sample-processor\n" + \
                "foo=bar\n" + \
                "sample-processor\n")
        self.assertEqual(wf.assignments, {'foo': 'bar'})
        self.assertEqual([str(x) for x in wf.steps], [
            'ocrd-sample-processor',
            'ocrd-sample-processor'
            ])

    def test_parse_line_continuation(self):
        wf = OcrdWf.parse(OCRD_WF_SHEBANG + "\n" +
                "ocrd-sample-processor\n" +
                "sample-processor \\\n" +
                "  -P foo bar \\\n" +
                "  # a comment interspersed\n" +
                "  -P bar foo\n")
        self.assertEqual([str(x) for x in wf.steps], [
            'ocrd-sample-processor',
            "ocrd-sample-processor -P foo '\"bar\"' -P bar '\"foo\"'"
            ])

if __name__ == "__main__":
    main(__file__)
