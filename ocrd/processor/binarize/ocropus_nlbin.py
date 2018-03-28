import subprocess
from ocrd.utils import mets_file_id
from ocrd.model.ocrd_page import OcrdPage
from ocrd.processor.base import Processor
from ocrd.constants import MIMETYPE_PAGE

class OcropusNlbinBinarizer(Processor):

    def process(self):
        for (input_file, n) in enumerate(self.input_files):
            self.workspace.download_file(input_file)
            page = OcrdPage.from_file(input_file)
            image_filename = self.workspace.download_url(page.imageFileName)
            subprocess.check_output([
                "ocropus-nlbin",
                image_filename
            ])
            self.add_output_file(
                ID=mets_file_id(self.outputGrp, n),
                input_file=input_file,
                mimetype=MIMETYPE_PAGE,
                content=image_filename.replace('.png', '.bin.png')
            )
