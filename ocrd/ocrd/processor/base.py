"""
Processor base class and helper functions
"""

__all__ = ['Processor', 'generate_processor_help', 'run_cli', 'run_processor']

import os
import json
from ocrd_utils import VERSION as OCRD_VERSION, MIMETYPE_PAGE
from ocrd_validators import ParameterValidator
from ocrd_models.ocrd_page import MetadataItemType, LabelType, LabelsType

# XXX imports must remain for backwards-compatibilty
from .helpers import run_cli, run_processor, generate_processor_help # pylint: disable=unused-import

class Processor():
    """
    A processor runs an algorithm based on the workspace, the mets.xml in the
    workspace (and the input files defined therein) as well as optional
    parameter.
    """

    def __init__(
            self,
            workspace,
            ocrd_tool=None,
            parameter=None,
            # TODO OCR-D/core#274
            # input_file_grp=None,
            # output_file_grp=None,
            input_file_grp="INPUT",
            output_file_grp="OUTPUT",
            page_id=None,
            show_help=False,
            show_version=False,
            dump_json=False,
            version=None
    ):
        if parameter is None:
            parameter = {}
        if dump_json:
            print(json.dumps(ocrd_tool, indent=True))
            return
        self.ocrd_tool = ocrd_tool
        if show_help:
            self.show_help()
            return
        self.version = version
        if show_version:
            self.show_version()
            return
        self.workspace = workspace
        # FIXME HACK would be better to use pushd_popd(self.workspace.directory)
        # but there is no way to do that in process here since it's an
        # overridden method. chdir is almost always an anti-pattern.
        if self.workspace:
            os.chdir(self.workspace.directory)
        self.input_file_grp = input_file_grp
        self.output_file_grp = output_file_grp
        self.page_id = None if page_id == [] or page_id is None else page_id
        parameterValidator = ParameterValidator(ocrd_tool)
        report = parameterValidator.validate(parameter)
        if not report.is_valid:
            raise Exception("Invalid parameters %s" % report.errors)
        self.parameter = parameter

    def show_help(self):
        print(generate_processor_help(self.ocrd_tool))

    def show_version(self):
        print("Version %s, ocrd/core %s" % (self.version, OCRD_VERSION))

    def verify(self):
        """
        Verify that the input fulfills the processor's requirements.
        """
        return True

    def process(self):
        """
        Process the workspace
        """
        raise Exception("Must be implemented")

    def add_metadata(self, pcgts):
        """
        Adds PAGE-XML MetadataItem describing the processing step
        """
        pcgts.get_Metadata().add_MetadataItem(
                MetadataItemType(type_="processingStep",
                    name=self.ocrd_tool['steps'][0],
                    value=self.ocrd_tool['executable'],
                    Labels=[LabelsType(
                        externalModel="ocrd-tool",
                        externalId="parameters",
                        Label=[LabelType(type_=name,
                            value=self.parameter[name])
                            for name in self.parameter.keys()])]))

    @property
    def input_files(self):
        """
        List the input files.

        - If there's a PAGE-XML for the page, take it (and forget about all
          other files for that page)
        - Else if there's only one image, take it (and forget about all other
          files for that page)
        - Otherwise raise an error (complaining that only PAGE-XML warrants

          having multiple images for a single page)
        (https://github.com/cisocrgroup/ocrd_cis/pull/57#issuecomment-656336593)
        """
        ret = self.workspace.mets.find_files(
            fileGrp=self.input_file_grp, pageId=self.page_id, mimetype=MIMETYPE_PAGE)
        if ret:
            return ret
        ret = self.workspace.mets.find_files(
            fileGrp=self.input_file_grp, pageId=self.page_id, mimetype="//image/.*")
        if self.page_id and len(ret) > 1:
            raise ValueError("No PAGE-XML %s in fileGrp '%s' but multiple images." % (
                "for page '%s'" % self.page_id if self.page_id else '',
                self.input_file_grp
                ))
        return ret
