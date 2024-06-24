# pylint: disable=missing-module-docstring,invalid-name
from os.path import join, basename

import click

from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_models.ocrd_page import to_xml
from ocrd_utils import (
    getLogger,
    assert_file_grp_cardinality,
    make_file_id,
    MIME_TO_EXT,
    MIMETYPE_PAGE,
    parse_json_string_with_comments,
    resource_string
)
from ocrd_modelfactory import page_from_file

OCRD_TOOL = parse_json_string_with_comments(resource_string(__package__ + '.dummy', 'ocrd-tool.json'))

class DummyProcessor(Processor):
    """
    Bare-bones processor creates PAGE-XML and optionally copies file from input group to output group
    """

    def process_page_pcgts(self, *input_pcgts):
        # nothing to do here
        return input_pcgts[0]

    def process_page_file(self, *input_files):
        LOG = getLogger('ocrd.dummy')
        input_file = input_files[0]
        if self.parameter['copy_files'] and input_file.mimetype != MIMETYPE_PAGE:
            # we need to mimic the actual copying in addition to the PAGE boilerplate
            file_id = make_file_id(input_file, self.output_file_grp)
            ext = MIME_TO_EXT.get(input_file.mimetype, '')
            local_filename = join(self.output_file_grp, file_id + ext)
            LOG.info("cp %s %s # %s -> %s", input_file.url, local_filename, input_file.ID, file_id)
            with open(input_file.local_filename, 'rb') as f:
                content = f.read()
                output_file = self.workspace.add_file(
                    file_id=file_id,
                    file_grp=self.output_file_grp,
                    page_id=input_file.pageId,
                    mimetype=input_file.mimetype,
                    local_filename=local_filename,
                    content=content)
            file_id = file_id + '_PAGE'
            pcgts = page_from_file(output_file)
            pcgts = self.process_page_pcgts(pcgts)
            pcgts.set_pcGtsId(file_id)
            self.add_metadata(pcgts)
            LOG.info("Add PAGE-XML %s generated for %s", file_id, output_file)
            self.workspace.add_file(file_id=file_id,
                                    file_grp=self.output_file_grp,
                                    page_id=input_file.pageId,
                                    local_filename=join(self.output_file_grp, file_id + '.xml'),
                                    mimetype=MIMETYPE_PAGE,
                                    content=to_xml(pcgts))

        else:
            if self.parameter['copy_files']:
                LOG.info("Not copying %s because it is a PAGE-XML file, which gets identity-transformed", input_file.local_filename)
            else:
                LOG.info("Not copying %s because it is not a PAGE-XML file and copy_files was false", input_file.local_filename)
            # we can rely on base implementation verbatim
            super().process_page_file(input_file)

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL['tools']['ocrd-dummy']
        kwargs['version'] = '0.0.3'
        super(DummyProcessor, self).__init__(*args, **kwargs)

    def setup(self):
        super().setup()
        assert_file_grp_cardinality(self.input_file_grp, 1)
        assert_file_grp_cardinality(self.output_file_grp, 1)

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)
