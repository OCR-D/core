# -*- coding: utf-8 -*-
from __future__ import absolute_import

import xml.etree.ElementTree as ET

import exiftool

from ocrd import init

ns = { 'mets'  : "http://www.loc.gov/METS/",
       'mods'  : "http://www.loc.gov/mods/v3",
       'xlink' : "http://www.w3.org/1999/xlink",
     }

class Characterizer:
    """
    Initializes an OCR process given a METS XML file.
    """

    def __init__(self):
        """
        The constructor.
        """

        self.clear()

    def clear(self):
        """
        Resets the Characterizer.
        """

        self.handle = init.Handle()

    def set_handle(self, handle):
        """
        (Re)sets the internal handle.
        """
        self.handle = handle

    def characterize(self):
        """
        Performs the image characterization.
        """
        with exiftool.ExifTool() as et:
            for ID in self.handle.img_files:
                # get XML for ID
                if ID in self.handle.page_trees:
                    PcGts = self.handle.page_trees[ID].getroot()
                    page = PcGts.find("Page")
                    if not page:
                        PcGts.append(ET.Element("Page"))
                        page = list(PcGts)[-1]
                    metadata = et.get_metadata(self.handle.img_files[ID])
                    page.set("imageWidth", "%d" % metadata["EXIF:ImageWidth"])
                    page.set("imageHeight", "%d" % metadata["EXIF:ImageHeight"])
                    page.set("imageXResolution", "%d" % metadata["EXIF:XResolution"])
                    page.set("imageYResolution", "%d" % metadata["EXIF:YResolution"])
