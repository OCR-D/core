# -*- coding: utf-8 -*-
from __future__ import absolute_import

import tesserocr
from PIL import Image

from lxml import etree as ET

from ocrd import init

ns = { 'mets'  : "http://www.loc.gov/METS/",
       'mods'  : "http://www.loc.gov/mods/v3",
       'xlink' : "http://www.w3.org/1999/xlink",
       'page'  : "http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15",
     }

class PageSegmenter:
    """
    Segments a page.
    """

    def __init__(self):
        """
        The constructor.
        """

        self.clear()

    def clear(self):
        """
        Resets the Segmenter.
        """

        self.handle = init.Handle()

    def set_handle(self, handle):
        """
        (Re)sets the internal handle.
        """
        self.handle = handle

    def _coords_from_box(self,box):
        """
        Constructs a polygon representation from a (rectangle) box
        """
        # tesseract uses a different region representation format
        return "%i,%i %i,%i %i,%i %i,%i" % (box['x'],box['y'],box['x']+box['w'],box['y']+box['w'],box['x']+box['w']+box['h'],box['y']+box['w']+box['h'],box['x']+box['h'],box['y']+box['h'])

    def segment(self):
        """
        Performs the segmentation.
        """
        with tesserocr.PyTessBaseAPI() as api:
            for ID in self.handle.img_files:
                image = Image.open(self.handle.img_files[ID])
                api.SetImage(image)
                boxes = api.GetComponentImages(tesserocr.RIL.BLOCK, True)
                if len(boxes) > 0:
                    # get XML for ID
                    if ID in self.handle.page_trees:
                        PcGts = self.handle.page_trees[ID].getroot()
                        pages = PcGts.xpath("page:Page", namespaces=ns)
                        if len(pages) > 0:
                            page = pages[0]
                        else:
                            page = ET.SubElement(PcGts,"Page")
                        reading_order = ET.SubElement(page,"ReadingOrder")
                    for i, (im, box, index, _) in enumerate(boxes):

                        # the region reference in the reading order element
                        region_ref = "r%i" % index
                        region_ref_indexed = ET.SubElement(reading_order,"RegionRefIndexed")
                        region_ref_indexed.set("regionRef", region_ref)
                        region_ref_indexed.set("index", "%i" % index)

                        # the actual region
                        region = ET.SubElement(page, "TextRegion")
                        region.set("id", region_ref)
                        coords = ET.SubElement(region, "Coords")
                        coords.set("points",self._coords_from_box(box))
