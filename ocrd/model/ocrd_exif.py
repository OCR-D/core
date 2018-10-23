import PIL

class OcrdExif(object):
    """
    Represents technical image metadata
    """

    @staticmethod
    def from_filename(image_filename):
        if image_filename is None:
            raise Exception("Must pass 'image_filename' to OcrdExif.from_filename")
        return OcrdExif(PIL.Image.open(image_filename))

    def __init__(self, img):
        #  print(img.__dict__)
        self.width = img.width
        self.height = img.height
        self.photometricInterpretation = img.mode
        for prop in ['compression', 'photometric_interpretation']:
            setattr(self, prop, img.info[prop] if prop in img.info else None)
        if img.format == 'TIFF' and 'dpi' in img.info:
            self.xResolution = img.info['dpi'][0]
            self.yResolution = img.info['dpi'][1]
            self.resolutionUnit = 'cm' if img.tag[296] == 3 else 'inches'
        elif img.format == 'JPEG':
            self.xResolution = img.info['jfif_density'][0]
            self.yResolution = img.info['jfif_density'][1]
            self.resolutionUnit = img.info['jfif_unit']
        elif img.format == 'PNG' and 'dpi' in img.info:
            self.xResolution = img.info['dpi'][0]
            self.yResolution = img.info['dpi'][1]
        else:
            #  if img.format == 'JPEG2000':
            #      import sys
            #      print('JPEG 2000 not supported yet :(', file=sys.stderr)
            self.xResolution = 1
            self.yResolution = 1
            self.resolutionUnit = 'inches'

    def to_xml(self):
        ret = '<exif>'
        for k in self.__dict__:
            ret += '<%s>%s</%s>' % (k, self.__dict__[k], k)
        ret += '</exif>'
        return ret
