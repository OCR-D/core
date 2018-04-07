import exiftool

EXIF_COMPRESSION_METHODS = {
    1: "Uncompressed",
    2: "CCITT 1D",
    3: "T4/Group 3 Fax",
    4: "T6/Group 4 Fax",
    5: "LZW",
    6: "JPEG (old-style)",
    7: "JPEG",
    8: "Adobe Deflate",
    9: "JBIG B&W",
    10: "JBIG Color",
    99: "JPEG",
    262: "Kodak 262",
    32766: "Next",
    32767: "Sony ARW Compressed",
    32769: "Packed RAW",
    32770: "Samsung SRW Compressed",
    32771: "CCIRLEW",
    32772: "Samsung SRW Compressed 2",
    32773: "PackBits",
    32809: "Thunderscan",
    32867: "Kodak KDC Compressed",
    32895: "IT8CTPAD",
    32896: "IT8LW",
    32897: "IT8MP",
    32898: "IT8BL",
    32908: "PixarFilm",
    32909: "PixarLog",
    32946: "Deflate",
    32947: "DCS",
    34661: "JBIG",
    34676: "SGILog",
    34677: "SGILog24",
    34712: "JPEG 2000",
    34713: "Nikon NEF Compressed",
    34715: "JBIG2 TIFF FX",
    34718: "Microsoft Document Imaging (MDI) Binary Level Codec",
    34719: "Microsoft Document Imaging (MDI) Progressive Transform Codec",
    34720: "Microsoft Document Imaging (MDI) Vector",
    34892: "Lossy JPEG",
    65000: "Kodak DCR Compressed",
    65535: "Pentax PEF Compressed",
}

EXIF_PHOTOMETRICINTERPRETATION_VALUES = {
    0: "WhiteIsZero",
    1: "BlackIsZero",
    2: "RGB",
    3: "RGB Palette",
    4: "Transparency Mask",
    5: "CMYK",
    6: "YCbCr",
    8: "CIELab",
    9: "ICCLab",
    10: "ITULab",
    32803: "Color Filter Array",
    32844: "Pixar LogL",
    32845: "Pixar LogLuv",
    34892: "Linear Raw",
}

EXIF_RESOLUTIONUNIT_VALUES = {
    2: "inches",
    3: "cm",
}

class OcrdExif(object):
    """
    Represents technical image metadata
    """

    @staticmethod
    def from_filename(image_filename):
        with exiftool.ExifTool() as et:
            exif_props = et.get_metadata(image_filename)
            return OcrdExif(exif_props)

    def __init__(self, props):
        self.width = props["EXIF:ImageWidth"]
        self.height = props["EXIF:ImageHeight"]
        self.xResolution = props["EXIF:XResolution"]
        self.yResolution = props["EXIF:YResolution"]
        self.compression = EXIF_COMPRESSION_METHODS.get(props["EXIF:Compression"], "Unknown")
        self.photometricInterpretation = EXIF_PHOTOMETRICINTERPRETATION_VALUES.get(props["EXIF:PhotometricInterpretation"], "Unknown")
        self.resolutionUnit = "%s" % EXIF_RESOLUTIONUNIT_VALUES.get(props["EXIF:ResolutionUnit"], "None")

    def to_xml(self):
        ret = '<exif>'
        for k in self.__dict__:
            ret += '<%s>%s</%s>' % (k, self.__dict__[k], k)
        ret += '</exif>'
        return ret
