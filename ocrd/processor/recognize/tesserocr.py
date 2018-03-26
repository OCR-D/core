from __future__ import absolute_import

from ocrd.model import OcrdPage
from ocrd.processor.base import Processor
from ocrd.utils import getLogger, mets_file_id
from ocrd.constants import MIMETYPE_PAGE

import tesserocr

log = getLogger('processor.Tesseract3Recognizer')

DEFAULT_PATH = tesserocr.get_languages()[0]
DEFAULT_MODEL = tesserocr.get_languages()[1][-1]

class Tesseract3Recognizer(Processor):

    def process(self):
        """
        Performs the (text) recognition.
        """
        with tesserocr.PyTessBaseAPI(path=DEFAULT_PATH, lang=DEFAULT_MODEL) as tessapi:
            tessapi.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
            for (n, input_file) in enumerate(self.input_files):
                page = OcrdPage.from_file(self.workspace.download_file(input_file))
                image_url = page.imageFileName
                for region_ref in page.text_region_refs:
                    log.info("About to recognize text in %i lines in '%s'", page.number_of_text_lines(parent=region_ref), region_ref)
                    for line_no in range(0, page.number_of_text_lines(parent=region_ref)):
                        log.debug("Recognizing text in region '%s' line '%s'", region_ref, line_no)
                        coords = page.get_text_line_coords(line_no, parent=region_ref)
                        # TODO use binarized / gray
                        image = self.workspace.resolve_image_as_pil(image_url, coords)
                        tessapi.SetImage(image)
                        content = tessapi.GetUTF8Text()
                        page.set_text_line_text_equiv(line_no, content, parent=region_ref)
                self.add_output_file(
                    ID=mets_file_id(self.outputGrp, n),
                    input_file=input_file,
                    mimetype=MIMETYPE_PAGE,
                    content=page.to_xml()
                )
