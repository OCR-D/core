import subprocess
from ocrd.utils import mets_file_id
from ocrd.model.ocrd_page import OcrdPage
from ocrd.processor.base import Processor
from ocrd.constants import MIMETYPE_PNG

class OcropusNlbinBinarizer(Processor):

    def process(self):
        for (n, input_file) in enumerate(self.input_files):
            self.workspace.download_file(input_file)
            page = OcrdPage.from_file(input_file)
            image_filename = self.workspace.download_url(page.imageFileName)
            subprocess.check_output([
                "ocropus-nlbin",
                image_filename
            ], cwd=self.workspace.directory)
            self.workspace.add_file(
                'OCR-D-IMG-BIN',
                ID=mets_file_id('OCR-D-IMG-BIN', n),
                mimetype=MIMETYPE_PNG,
                local_filename="%s.%s" % (input_file.basename_without_extension, 'bin.png')
            )
            self.workspace.add_file(
                'OCR-D-IMG-NRM',
                ID=mets_file_id('OCR-D-IMG-NRM', n),
                mimetype=MIMETYPE_PNG,
                local_filename="%s.%s" % (input_file.basename_without_extension, 'nrm.png')
            )
