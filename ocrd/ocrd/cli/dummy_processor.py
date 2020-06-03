# pylint: disable=missing-module-docstring,invalid-name
from os.path import join, basename

import click

from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_utils import getLogger

DUMMY_TOOL = {
    'executable': 'ocrd-dummy',
    'description': 'Bare-bones processor that copies file from input group to output group',
    'steps': ['preprocessing/optimization'],
    'categories': ['Image preprocessing'],
    'input_file_grp': 'DUMMY_INPUT',
    'output_file_grp': 'DUMMY_OUTPUT',
}

LOG = getLogger('ocrd.dummy')

class DummyProcessor(Processor):
    """
    Bare-bones processor that copies mets:file from input group to output group.
    """

    def process(self):
        for n, input_file in enumerate(self.input_files):
            input_file = self.workspace.download_file(input_file)
            page_id = input_file.pageId or input_file.ID
            LOG.info("INPUT FILE %i / %s", n, page_id)
            file_id = 'COPY_OF_%s' % input_file.ID
            local_filename = join(self.output_file_grp, basename(input_file.local_filename))
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
        kwargs['ocrd_tool'] = DUMMY_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)
