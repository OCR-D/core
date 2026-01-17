# pylint: disable=missing-module-docstring,invalid-name
from typing import List, Optional, get_args
import os
import subprocess
from tempfile import TemporaryDirectory

import click

from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd import Processor
from ocrd.processor.base import MissingInputFile
from ocrd_models import OcrdPage, OcrdFileType
from ocrd_models.ocrd_page import to_xml
from ocrd_modelfactory import page_from_file
from ocrd_utils import config, make_file_id, MIMETYPE_PAGE


class ShellProcessor(Processor):

    def setup(self):
        command = self.parameter['command']
        if '@INFILE' not in command:
            raise Exception("command parameter requires @INFILE pattern")
        if '@OUTFILE' not in command:
            raise Exception("command parameter requires @OUTFILE pattern")

    def process_page_file(self, *input_files: Optional[OcrdFileType]) -> None:
        """
        Process PAGE files via arbitrary command line on the shell.

        \b
        For each selected physical page of the workspace, pass ``command`` 
        to the shell, replacing:
        - the string ``@INFILE`` with the PAGE input file path,
        - the string ``@OUTFILE`` with the PAGE output file path.

        Modify the resulting PAGE output file with our new `@pcGtsId` and
        metadata.
        """
        input_paths: List[str] = [""] * len(input_files)
        input_pos = next(i for i, input_file in enumerate(input_files)
                         if input_file is not None)
        page_id = input_files[input_pos].pageId
        self._base_logger.info("processing page %s", page_id)
        for i, input_file in enumerate(input_files):
            grp = self.input_file_grp.split(',')[i]
            if input_file is None:
                self._base_logger.debug(f"ignoring missing file for input fileGrp {grp} for page {page_id}")
                continue
            assert isinstance(input_file, get_args(OcrdFileType))
            if not input_file.local_filename:
                self._base_logger.error(f'No local file exists for page {page_id} in file group {grp}')
                if config.OCRD_MISSING_INPUT == 'ABORT':
                    raise MissingInputFile(grp, page_id, input_file.mimetype)
                continue
            self._base_logger.debug(f"parsing file {input_file.ID} for page {page_id}")
            if os.path.exists(input_file.local_filename):
                input_paths[i] = input_file.local_filename
            else:
                self._base_logger.error(f"non-existing local file for input fileGrp {grp} for page {page_id}")
        if not any(input_paths):
            self._base_logger.warning(f'skipping page {page_id}')
            return
        output_file_id = make_file_id(input_files[input_pos], self.output_file_grp)
        if input_files[input_pos].fileGrp == self.output_file_grp:
            # input=output fileGrp: re-use ID exactly
            output_file_id = input_files[input_pos].ID
        output_file = next(self.workspace.mets.find_files(ID=output_file_id), None)
        if output_file and config.OCRD_EXISTING_OUTPUT != 'OVERWRITE':
            # short-cut avoiding useless computation:
            raise FileExistsError(
                f"A file with ID=={output_file_id} already exists {output_file} and neither force nor ignore are set"
            )
        command = self.parameter['command']
        with TemporaryDirectory(suffix=page_id) as tmpdir:
            out_path = os.path.join(tmpdir, output_file_id + ".xml")
            # remove quotation around filename patterns, if any
            command = command.replace('"@INFILE"', '@INFILE').replace('"@OUTFILE"', '@OUTFILE')
            command = command.replace("'@INFILE'", '@INFILE').replace("'@OUTFILE'", '@OUTFILE')
            # replace filename patterns with actual paths, quoted
            for in_path in input_paths:
                command = command.replace('@INFILE', '"' + in_path + '"', 1)
            command = command.replace('@OUTFILE', '"' + out_path + '"')
            # execute command pattern
            self.logger.debug("Running command: '%s'", command)
            # pylint: disable=subprocess-run-check
            result = subprocess.run(command, shell=True,
                                    universal_newlines=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            self.logger.debug("Command for %s returned: %d", page_id, result.returncode)
            if result.stdout:
                self.logger.info("Command for %s stdout: %s", page_id, result.stdout)
            if result.stderr:
                self.logger.warning("Command for %s stderr: %s", page_id, result.stderr)
            if result.returncode != 0:
                self.logger.error("Command for %s failed", page_id)
                return
            try:
                result = page_from_file(out_path)
                assert isinstance(result, OcrdPage)
            except ValueError as err:
                # not PAGE and not an image to generate PAGE for
                self._base_logger.error(f"non-PAGE output for page {page_id}: {err}")
                return
        result.set_pcGtsId(output_file_id)
        self.add_metadata(result)
        self.workspace.add_file(
            file_id=output_file_id,
            file_grp=self.output_file_grp,
            page_id=page_id,
            local_filename=os.path.join(self.output_file_grp, output_file_id + '.xml'),
            mimetype=MIMETYPE_PAGE,
            content=to_xml(result),
        )

    @property
    def metadata_filename(self):
        return 'processor/builtin/dummy/ocrd-tool.json'

    @property
    def executable(self):
        return 'ocrd-command'


@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(ShellProcessor, *args, **kwargs)
