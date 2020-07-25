# pylint: disable=missing-module-docstring,invalid-name
from os.path import join, basename
from pkg_resources import resource_string

import click

from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_utils import (
    getLogger,
    assert_file_grp_cardinality,
    make_file_id,
    MIME_TO_EXT,
    parse_json_string_with_comments
)

OCRD_TOOL = parse_json_string_with_comments(resource_string(__name__, 'dummy/ocrd-tool.json').decode('utf8'))

LOG = getLogger('ocrd.dummy')

class DummyProcessor(Processor):
    """
    Bare-bones processor that copies mets:file from input group to output group.
    """

    def process(self):
        assert_file_grp_cardinality(self.input_file_grp, 1)
        assert_file_grp_cardinality(self.output_file_grp, 1)
        for input_file in self.input_files:
            input_file = self.workspace.download_file(input_file)
            file_id = make_file_id(input_file, self.output_file_grp)
            ext = MIME_TO_EXT.get(input_file.mimetype, '')
            local_filename = join(self.output_file_grp, file_id + ext)
            LOG.info("cp %s %s # %s -> %s", input_file.url, local_filename, input_file.ID, file_id)
            with open(input_file.local_filename, 'rb') as f:
                content = f.read()
                self.workspace.add_file(
                    ID=file_id,
                    file_grp=self.output_file_grp,
                    pageId=input_file.pageId,
                    mimetype=input_file.mimetype,
                    local_filename=local_filename,
                    content=content)

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)
