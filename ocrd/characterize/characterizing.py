# -*- coding: utf-8 -*-
from __future__ import absolute_import

import xml.etree.ElementTree as ET

import exiftool, json

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
            for img in self.handle.img_files:
                metadata = et.get_metadata(self.handle.img_files[img])
                print(json.dumps(metadata, sort_keys=True, indent=4))
