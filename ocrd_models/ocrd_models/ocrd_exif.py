"""
Technical image metadata
"""

class OcrdExif():
    """
    Represents technical image metadata
    """

    def __init__(self, img):
        """
        Arguments:
            img (PIL.Image): PIL image technical metadata is about.
        """
        #  print(img.__dict__)
        self.width = img.width
        self.height = img.height
        self.photometricInterpretation = img.mode
        #  if img.format == 'PNG':
        #      print(img.info)
        for prop in ['compression', 'photometric_interpretation']:
            setattr(self, prop, img.info[prop] if prop in img.info else None)
        if img.format in ('TIFF', 'PNG') and 'dpi' in img.info:
            self.xResolution = img.info['dpi'][0]
            self.yResolution = img.info['dpi'][1]
            self.resolutionUnit = 'cm' if img.tag[296] == 3 else 'inches'
        elif img.format == 'JPEG':
            self.xResolution = img.info['jfif_density'][0]
            self.yResolution = img.info['jfif_density'][1]
            self.resolutionUnit = img.info['jfif_unit']
        elif img.format == 'PNG' and 'aspect' in img.info:
            self.xResolution = img.info['aspect'][0]
            self.yResolution = img.info['aspect'][1]
        else:
            #  if img.format == 'JPEG2000':
            #      import sys
            #      print('JPEG 2000 not supported yet :(', file=sys.stderr)
            self.xResolution = 1
            self.yResolution = 1
            self.resolutionUnit = 'inches'

    def to_xml(self):
        """
        Serialize all properties as XML
        """
        ret = '<exif>'
        for k in self.__dict__:
            ret += '<%s>%s</%s>' % (k, self.__dict__[k], k)
        ret += '</exif>'
        return ret
