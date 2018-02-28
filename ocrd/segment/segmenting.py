# -*- coding: utf-8 -*-
from __future__ import absolute_import

import tesserocr,numpy,cv2
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
    Segments a page into regions.
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

    def _points_from_box(self,box):
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
                        coords.set("points",self._points_from_box(box))

class RegionSegmenter:
    """
    Segments a region into lines.
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

    def _polygon_from_points(self, points):
        """
        Constructs a numpy-compatible polygon from a page representation.
        """
        polygon = []
        for pair in points.split(" "):
            x_y = pair.split(",")
            polygon.append([float(x_y[0]),float(x_y[1])])
        return polygon

    def _points_from_box(self,box):
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
                image = cv2.imread(self.handle.img_files[ID])
                if ID in self.handle.page_trees:
                    PcGts = self.handle.page_trees[ID].getroot()
                    pages = PcGts.xpath("page:Page", namespaces=ns)
                    for page in pages[0:1]:
                        regions = page.xpath("TextRegion")
                        for region in regions:
                            points = region.xpath("Coords")[0].get("points")
                            polygon = self._polygon_from_points(points)
                            poly = numpy.array(polygon,numpy.int32)
                            region_cut = image[numpy.min(poly[:,1]):numpy.max(poly[:,1]),numpy.min(poly[:,0]):numpy.max(poly[:,0])]
                            region_img = Image.fromarray(region_cut)
                            api.SetImage(region_img)
                            lines = api.GetComponentImages(tesserocr.RIL.TEXTLINE, True)
                            for i, (im, box, index, _) in enumerate(lines):
                                line = ET.SubElement(region, "TextLine")
                                coords = ET.SubElement(line, "Coords")
                                coords.set("points",self._points_from_box(box))
