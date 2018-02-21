# -*- coding: utf-8 -*-
from __future__ import absolute_import

import exiftool

from lxml import etree as ET

from ocrd import init

ns = { 'mets'  : "http://www.loc.gov/METS/",
       'mods'  : "http://www.loc.gov/mods/v3",
       'xlink' : "http://www.w3.org/1999/xlink",
       'page'  : "http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15",
     }

exif_compression_methods = {
        1	: "Uncompressed",
        2	: "CCITT 1D",
        3	: "T4/Group 3 Fax",
        4	: "T6/Group 4 Fax",
        5	: "LZW",
        6	: "JPEG (old-style)",
        7	: "JPEG",
        8	: "Adobe Deflate",
        9	: "JBIG B&W",
        10	: "JBIG Color",
        99	: "JPEG",
        262	: "Kodak 262",
        32766	: "Next",
        32767	: "Sony ARW Compressed",
        32769	: "Packed RAW",
        32770	: "Samsung SRW Compressed",
        32771	: "CCIRLEW",
        32772	: "Samsung SRW Compressed 2",
        32773	: "PackBits",
        32809	: "Thunderscan",
        32867	: "Kodak KDC Compressed",
        32895	: "IT8CTPAD",
        32896	: "IT8LW",
        32897	: "IT8MP",
        32898	: "IT8BL",
        32908	: "PixarFilm",
        32909	: "PixarLog",
        32946	: "Deflate",
        32947	: "DCS",
        34661	: "JBIG",
        34676	: "SGILog",
        34677	: "SGILog24",
        34712	: "JPEG 2000",
        34713	: "Nikon NEF Compressed",
        34715	: "JBIG2 TIFF FX",
        34718	: "Microsoft Document Imaging (MDI) Binary Level Codec",
        34719	: "Microsoft Document Imaging (MDI) Progressive Transform Codec",
        34720	: "Microsoft Document Imaging (MDI) Vector",
        34892	: "Lossy JPEG",
        65000	: "Kodak DCR Compressed",
        65535	: "Pentax PEF Compressed",
    }

exif_photometricinterpretation_values = {
        0     : "WhiteIsZero",
        1     : "BlackIsZero",
        2     : "RGB",
        3     : "RGB Palette",
        4     : "Transparency Mask",
        5     : "CMYK",
        6     : "YCbCr",
        8     : "CIELab",
        9     : "ICCLab",
        10    : "ITULab",
        32803 : "Color Filter Array",
        32844 : "Pixar LogL",
        32845 : "Pixar LogLuv",
        34892 : "Linear Raw",
    }

exif_resolutionunit_values = {
        2 : "inches",
        3 : "cm", 
    }

class Characterizer:
    """
    Extracts image meta data.
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
                    pages = PcGts.xpath("page:Page", namespaces=ns)
                    if len(pages) > 0:
                        page = pages[0]
                    else:
                        page = ET.SubElement(PcGts,"Page")
                    metadata = et.get_metadata(self.handle.img_files[ID])
                    page.set("imageWidth", "%d" % metadata.get("EXIF:ImageWidth",""))
                    page.set("imageHeight", "%d" % metadata.get("EXIF:ImageHeight",""))
                    page.set("imageXResolution", "%d" % metadata.get("EXIF:XResolution"))
                    page.set("imageYResolution", "%d" % metadata.get("EXIF:YResolution",""))
                    page.set("imageCompression", "%s" % exif_compression_methods.get(metadata.get("EXIF:Compression",0),"Unknown"))
                    page.set("imagePhotometricInterpretation", "%s" % exif_photometricinterpretation_values.get(metadata.get("EXIF:PhotometricInterpretation",0),"Unknown"))
                    page.set("imageResolutionUnit", "%s" % exif_resolutionunit_values.get(metadata.get("EXIF:ResolutionUnit",1),"None"))
