from ocrd.model import OcrdPage
from ocrd.processor import Processor
from ocrd.utils import getLogger
from ocrd.constants import MIMETYPE_PAGE

import tesserocr
import cv2
import PIL
import numpy as np

log = getLogger('processor.segment_line.tesseract3')

class Tesseract3LineSegmenter(Processor):

    def process(self):
        """
        Performs the line segmentation.
        """
        with tesserocr.PyTessBaseAPI() as tessapi:
            for input_file in self.input_files:
                #  print(input_file)
                self.workspace.download_file(input_file)
                page = OcrdPage.from_file(input_file)
                image_filename = self.workspace.download_url(page.imageFileName)
                image = cv2.imread(image_filename)
                log.debug("Detecting text lines with tesseract")
                for region_ref in page.text_region_refs:
                    poly = np.array(page.get_region_coords(region_ref), np.int32)
                    region_cut = image[
                        np.min(poly[:, 1]):np.max(poly[:, 1]),
                        np.min(poly[:, 0]):np.max(poly[:, 0])
                    ]
                    region_img = PIL.Image.fromarray(region_cut)
                    tessapi.SetImage(region_img)
                    for component in tessapi.GetComponentImages(tesserocr.RIL.TEXTLINE, True):
                        page.add_text_line(component[1], parent=region_ref)
                self.add_output_file(input_file=input_file, mimetype=MIMETYPE_PAGE, content=page.to_xml())
