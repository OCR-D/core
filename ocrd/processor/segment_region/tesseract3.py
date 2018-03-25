from ocrd.model import OcrdPage
from ocrd.processor.base import Processor
from ocrd.utils import getLogger
from ocrd.constants import MIMETYPE_PAGE

import tesserocr

log = getLogger('processor.segment_region.tesseract3')

class Tesseract3RegionSegmenter(Processor):

    def process(self):
        """
        Performs the region segmentation.
        """
        with tesserocr.PyTessBaseAPI() as tessapi:
            for input_file in self.input_files:
                page = OcrdPage.from_file(self.workspace.download_file(input_file))
                image = self.workspace.resolve_image_as_pil(page.imageFileName)
                log.debug("Detecting regions with tesseract")
                tessapi.SetImage(image)
                for component in tessapi.GetComponentImages(tesserocr.RIL.BLOCK, True):
                    box, index = component[1], component[2]
                    # the region reference in the reading order element
                    region_ref = "r%i" % index
                    page.add_reading_order_ref(region_ref, index)
                    page.add_text_region(region_ref, box)
                self.add_output_file(input_file=input_file, mimetype=MIMETYPE_PAGE, content=page.to_xml())
