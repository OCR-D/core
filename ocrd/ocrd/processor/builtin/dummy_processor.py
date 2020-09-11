# pylint: disable=missing-module-docstring,invalid-name
from os.path import join, basename
from pkg_resources import resource_string

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
    parse_json_string_with_comments
)
from ocrd_modelfactory import page_from_file

OCRD_TOOL = parse_json_string_with_comments(resource_string(__name__, 'dummy/ocrd-tool.json').decode('utf8'))

class DummyProcessor(Processor):
    """
    Bare-bones processor that copies mets:file from input group to output group.
    """

    def process(self):
        LOG = getLogger('ocrd.dummy')
        assert_file_grp_cardinality(self.input_file_grp, 1)
        assert_file_grp_cardinality(self.output_file_grp, 1)
        for input_file in self.input_files:
            input_file = self.workspace.download_file(input_file)
            file_id = make_file_id(input_file, self.output_file_grp)
            ext = MIME_TO_EXT.get(input_file.mimetype, '')
            local_filename = join(self.output_file_grp, file_id + ext)
            pcgts = page_from_file(self.workspace.download_file(input_file))
            self.add_metadata(pcgts)
            LOG.info("cp %s %s # %s -> %s", input_file.url, local_filename, input_file.ID, file_id)
            if input_file.mimetype == MIMETYPE_PAGE:
                # Source file is PAGE-XML: Write out in-memory PcGtsType
                self.workspace.add_file(
                    ID=file_id,
                    file_grp=self.output_file_grp,
                    pageId=input_file.pageId,
                    mimetype=input_file.mimetype,
                    local_filename=local_filename,
                    content=to_xml(pcgts).encode('utf-8'))
            else:
                # Source file is not PAGE-XML: Copy byte-by-byte
                with open(input_file.local_filename, 'rb') as f:
                    content = f.read()
                    self.workspace.add_file(
                        ID=file_id,
                        file_grp=self.output_file_grp,
                        pageId=input_file.pageId,
                        mimetype=input_file.mimetype,
                        local_filename=local_filename,
                        content=content)
                if input_file.mimetype.startswith('image/'):
                    # write out the PAGE-XML representation for this image
                    page_file_id = file_id + '_PAGE'
                    pcgts.set_pcGtsId(page_file_id)
                    pcgts.get_Page().set_imageFilename(local_filename)
                    page_filename = join(self.output_file_grp, file_id + '.xml')
                    LOG.info("Add PAGE-XML %s generated for %s at %s",
                             page_file_id, file_id, page_filename)
                    self.workspace.add_file(
                        ID=page_file_id,
                        file_grp=self.output_file_grp,
                        pageId=input_file.pageId,
                        mimetype=MIMETYPE_PAGE,
                        local_filename=page_filename,
                        content=to_xml(pcgts).encode('utf-8'))


    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL
        kwargs['version'] = '0.0.1'
        super(DummyProcessor, self).__init__(*args, **kwargs)

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)
