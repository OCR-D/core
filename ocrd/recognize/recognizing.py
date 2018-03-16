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

class Recognizer:
    """
    Recognizes text in lines.
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
        self.path = (tesserocr.get_languages()[0])

    def set_handle(self, handle):
        """
        (Re)sets the internal handle.
        """
        self.handle = handle

    def set_model(self,path=tesserocr.get_languages()[0],model=tesserocr.get_languages()[1][-1]):
        """
        (Re)sets the search path for recognition models.
        """
        self.path = path
        self.model = model

    def _polygon_from_points(self, points):
        """
        Constructs a numpy-compatible polygon from a page representation.
        """
        polygon = []
        for pair in points.split(" "):
            x_y = pair.split(",")
            polygon.append([float(x_y[0]),float(x_y[1])])
        return polygon

    def recognize(self):
        """
        Performs the (text) recognition.
        """
        with tesserocr.PyTessBaseAPI(path=self.path,lang=self.model) as api:
            api.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
            for ID in self.handle.page_trees:
                if ID in self.handle.img_files:
                    image = cv2.imread(self.handle.img_files[ID])
                    PcGts = self.handle.page_trees[ID].getroot()
                    pages = PcGts.xpath("page:Page", namespaces=ns)
                    for page in pages[0:1]:
                        regions = page.xpath("TextRegion")
                        for region in regions:
                            lines = region.xpath("TextLine")
                            for line in lines:
                                points = line.xpath("Coords")[0].get("points")
                                polygon = self._polygon_from_points(points)
                                poly = numpy.array(polygon,numpy.int32)
                                line_cut = image[numpy.min(poly[:,1]):numpy.max(poly[:,1]),numpy.min(poly[:,0]):numpy.max(poly[:,0])]
                                line_img = Image.fromarray(line_cut)
                                api.SetImage(line_img)
                                text = ET.SubElement(line, "TextEquiv")
                                content = api.GetUTF8Text()
                                print(content)
                                text.text = content
            pass
