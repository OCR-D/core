# -*- coding: utf-8 -*-
from __future__ import absolute_import
#  import re
import exiftool

from ocrd.constants import EXIF_COMPRESSION_METHODS, EXIF_PHOTOMETRICINTERPRETATION_VALUES, EXIF_RESOLUTIONUNIT_VALUES
from ocrd.processor.base import Processor
from ocrd.model.ocrd_page import OcrdPage

class ExifProcessor(Processor):
    """
    Extracts image meta data.
    """

    def verify(self):
        """
        Ensure that the output is only pages
        """
        return True

    def process(self):
        """
        Performs the image characterization.
        """
        with exiftool.ExifTool() as et:
            for input_file in self.workspace.mets.find_files(fileGrp='INPUT'):
                self.workspace.download_file(input_file)
                page = OcrdPage.from_file(input_file)
                image_filename = self.workspace.download_url(page.imageFileName)
                exif_props = et.get_metadata(image_filename)
                page.imageWidth = "%d" % exif_props.get("EXIF:ImageWidth", "")
                page.imageHeight = "%d" % exif_props.get("EXIF:ImageHeight", "")
                page.imageXResolution = "%d" % exif_props.get("EXIF:XResolution")
                page.imageYResolution = "%d" % exif_props.get("EXIF:YResolution", "")
                page.imageCompression = "%s" % EXIF_COMPRESSION_METHODS.get(
                    exif_props.get("EXIF:Compression", 0), "Unknown")
                page.imagePhotometricInterpretation = "%s" % EXIF_PHOTOMETRICINTERPRETATION_VALUES.get(
                    exif_props.get("EXIF:PhotometricInterpretation", 0), "Unknown")
                page.imageResolutionUnit = "%s" % EXIF_RESOLUTIONUNIT_VALUES.get(
                    exif_props.get("EXIF:ResolutionUnit", 1), "None")
                self.workspace.add_file(
                    'OUTPUT',
                    basename=input_file.basename_without_extension + '.xml',
                    content=page.to_xml()
                )
