from ocrd.model import OcrdPage
from ocrd.processor.base import Processor
from ocrd.utils import getLogger
from ocrd.constants import MIMETYPE_PAGE

import tesserocr

log = getLogger('processor.segment_line.tesseract3')

class Tesseract3LineSegmenter(Processor):

    def process(self):
        """
        Performs the line segmentation.
        """
        with tesserocr.PyTessBaseAPI() as tessapi:
            for input_file in self.input_files:
                page = OcrdPage.from_file(self.workspace.download_file(input_file))
                image_url = page.imageFileName
                for region_ref in page.text_region_refs:
                    log.debug("Detecting lines in %s with tesseract", region_ref)
                    coords = page.get_region_coords(region_ref)
                    image = self.workspace.resolve_image_as_pil(image_url, coords)
                    tessapi.SetImage(image)
                    for component in tessapi.GetComponentImages(tesserocr.RIL.TEXTLINE, True):
                        page.add_text_line(component[1], parent=region_ref)
                self.add_output_file(input_file=input_file, mimetype=MIMETYPE_PAGE, content=page.to_xml())
