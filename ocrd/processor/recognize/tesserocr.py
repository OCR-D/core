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
            log.info("Using model %s in %s for recognition", tesserocr.get_languages()[0], tesserocr.get_languages()[1][-1])
            tessapi.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
            for (n, input_file) in enumerate(self.input_files):
                log.info("INPUT FILE %i / %s", n, input_file)
                self.workspace.download_file(input_file)
                page = OcrdPage.from_file(input_file)
                image_url = page.imageFileName
                log.info("page %s", page)
                for region in page.list_textregions():
                    textlines = region.list_textlines()
                    log.info("About to recognize text in %i lines of region '%s'", len(textlines), region.ID)
                    for (line_no, line) in enumerate(textlines):
                        log.debug("Recognizing text in region '%s' line '%s'", region.ID, line_no)
                        # TODO use binarized / gray
                        image = self.workspace.resolve_image_as_pil(image_url, line.coords)
                        tessapi.SetImage(image)
                        line.textequiv = tessapi.GetUTF8Text()
                self.add_output_file(
                    ID=mets_file_id(self.outputGrp, n),
                    input_file=input_file,
                    mimetype=MIMETYPE_PAGE,
                    content=page.to_xml()
                )
