"""
Technical image metadata
"""

from math import sqrt
from io import BytesIO
from subprocess import run, PIPE
from distutils.spawn import find_executable as which

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
        if img.format == 'JPEG2000':
            # XXX find a way to get pixel density in jpeg2000
            self.xResolution = self.yResolution = 1
            self.resolutionUnit = 'inches'
        else:
            if img.filename:
                ret = run(['identify', '-format', r'%x %y %U', img.filename], check=False, stderr=PIPE, stdout=PIPE)
            else:
                with BytesIO() as bio:
                    img.save(bio, format=img.format)
                    ret = run(['identify', '-format', r'%x %y %U', '/dev/stdin'], check=False, stderr=PIPE, stdout=PIPE, input=bio.getvalue())
            if ret.returncode:
                if not which('identify'):
                    raise Exception("The 'identify' command is not available. Install with 'sudo apt install imagemagick'")
                raise ValueError("'identify' returned non-zero exit code %s. stderr: %s" % (ret.returncode, ret.stderr))
            tokens = ret.stdout.decode('utf-8').split(' ', 3)
            self.xResolution = int(float(tokens[0]))
            self.yResolution = int(float(tokens[1]))
            self.resolutionUnit = 'inches' if tokens[2] == 'undefined' else \
                                  'cm' if tokens[2] == 'PixelsPerCentimeter' else \
                                  'inches'
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
