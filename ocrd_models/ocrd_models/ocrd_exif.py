"""
Technical image metadata
"""

from math import sqrt

class OcrdExif():
    """Represents technical image metadata.

    Members:

    - `width` / `height`: pixel dimensions
    - `photometricInterpretation`: pixel type/depth, e.g.
      '1' for b/w,
      'L' for 8-bit grayscale,
      'RGB' for 24-bit truecolor,
      'I' for 32-bit signed integer grayscale,
      'F' for floating-point grayscale
      (see PIL concept `mode`)
    - `resolution` / `xResolution` / `yResolution`: pixel density
    - `resolutionUnit`: unit of measurement (either `inches` or `cm`)

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
        self.n_frames = img.n_frames if 'n_frames' in img.__dict__ else 1
        #  if img.format == 'PNG':
        #      print(img.info)
        for prop in ['compression', 'photometric_interpretation']:
            setattr(self, prop, img.info[prop] if prop in img.info else None)
        if img.format in ('TIFF', 'PNG') and 'dpi' in img.info:
            self.xResolution = int(img.info['dpi'][0])
            self.yResolution = int(img.info['dpi'][1])
            if img.format == 'TIFF':
                self.resolutionUnit = 'cm' if img.tag.get(296) == 3 else 'inches'
            else:
                self.resolutionUnit = 'inches'
        elif img.format == 'JPEG' and 'jfif_density' in img.info:
            self.xResolution = img.info['jfif_density'][0]
            self.yResolution = img.info['jfif_density'][1]
            self.resolutionUnit = 'cm' if img.info['jfif_unit'] == 2 else 'inches'
        elif img.format == 'PNG' and 'aspect' in img.info:
            self.xResolution = img.info['aspect'][0]
            self.yResolution = img.info['aspect'][1]
            self.resolutionUnit = 'inches'
        else:
            #  if img.format == 'JPEG2000':
            #      import sys
            #      print('JPEG 2000 not supported yet :(', file=sys.stderr)
            self.xResolution = 1
            self.yResolution = 1
            self.resolutionUnit = 'inches'
        #  print('format=%s type=%s' % (img.format, type(self.xResolution))
        self.resolution = round(sqrt(self.xResolution * self.yResolution))

    def to_xml(self):
        """
        Serialize all properties as XML
        """
        ret = '<exif>'
        for k in self.__dict__:
            ret += '<%s>%s</%s>' % (k, self.__dict__[k], k)
        ret += '</exif>'
        return ret
