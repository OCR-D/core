# pylint: disable=missing-module-docstring,invalid-name
from os.path import join
from typing import Optional

import click

from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd.processor.ocrd_page_result import OcrdPageResult
from ocrd_models.ocrd_file import OcrdFileType
from ocrd_models.ocrd_page import OcrdPage, to_xml
from ocrd_utils import (
    make_file_id,
    MIME_TO_EXT,
    MIMETYPE_PAGE,
    parse_json_string_with_comments,
    resource_string,
    config
)
from ocrd_modelfactory import page_from_file

class DummyProcessor(Processor):
    """
    Bare-bones processor creates PAGE-XML and optionally copies file from input group to output group
    """

    def process_page_pcgts(self, *input_pcgts: Optional[OcrdPage], page_id: Optional[str] = None) -> OcrdPageResult:
        assert input_pcgts[0]
        # nothing to do here
        return OcrdPageResult(input_pcgts[0])

    def process_page_file(self, *input_files: Optional[OcrdFileType]) -> None:
        input_file = input_files[0]
        assert input_file
        assert input_file.local_filename
        if self.parameter['copy_files'] and input_file.mimetype != MIMETYPE_PAGE:
            # we need to mimic the actual copying in addition to the PAGE boilerplate
            file_id = make_file_id(input_file, self.output_file_grp)
            ext = MIME_TO_EXT.get(input_file.mimetype, '')
            local_filename = join(self.output_file_grp, file_id + ext)
            self.logger.info("cp %s %s # %s -> %s", input_file.url, local_filename, input_file.ID, file_id)
            with open(input_file.local_filename, 'rb') as f:
                output_file = self.workspace.add_file(
                    file_id=file_id,
                    file_grp=self.output_file_grp,
                    page_id=input_file.pageId,
                    mimetype=input_file.mimetype,
                    local_filename=local_filename,
                    content=f.read(),
                    force=config.OCRD_EXISTING_OUTPUT == 'OVERWRITE',
                )
            file_id = file_id + '_PAGE'
            pcgts = page_from_file(output_file)
            assert isinstance(pcgts, OcrdPage)
            pcgts = self.process_page_pcgts(pcgts).pcgts
            pcgts.set_pcGtsId(file_id)
            self.add_metadata(pcgts)
            self.logger.info("Add PAGE-XML %s generated for %s", file_id, output_file)
            self.workspace.add_file(file_id=file_id,
                                    file_grp=self.output_file_grp,
                                    page_id=input_file.pageId,
                                    local_filename=join(self.output_file_grp, file_id + '.xml'),
                                    mimetype=MIMETYPE_PAGE,
                                    content=to_xml(pcgts),
                                    force=config.OCRD_EXISTING_OUTPUT == 'OVERWRITE',
            )
        else:
            if self.parameter['copy_files']:
                self.logger.info("Not copying %s because it is a PAGE-XML file, which gets identity-transformed", input_file.local_filename)
            else:
                self.logger.info("Not copying %s because it is not a PAGE-XML file and copy_files was false", input_file.local_filename)
            # we can rely on base implementation verbatim
            super().process_page_file(input_file)

    @property
    def metadata_filename(self):
        return 'processor/builtin/dummy/ocrd-tool.json'

    @property
    def executable(self):
        return 'ocrd-dummy'

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(DummyProcessor, *args, **kwargs)
