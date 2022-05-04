"""
Technical image metadata
"""

from math import sqrt
from io import BytesIO
from subprocess import run, PIPE
from distutils.spawn import find_executable as which
from ocrd_utils import getLogger

class OcrdExif():
    """Represents technical image metadata.

    Attributes:
        width (int): pixel dimensions
        height (int): pixel dimensions
        photometricInterpretation (str): pixel type/depth, e.g. \

            * ``1`` for b/w,
            * ``L`` for 8-bit grayscale,
            * ``RGB`` for 24-bit truecolor,
            * ``I`` for 32-bit signed integer grayscale,
            * ``F`` for floating-point grayscale
          (see PIL concept **mode**)
        resolution (int): pixel density
        xResolution (int): pixel density
        yResolution (int): pixel density
        resolutionUnit (str): unit of measurement (either ``inches`` or ``cm``)
    """

    def __init__(self, img):
        """
        Arguments:
            img (`PIL.Image`): PIL image technical metadata is about.
        """
        #  print(img.__dict__)
        self.width = img.width
        self.height = img.height
        self.photometricInterpretation = img.mode
        self.n_frames = img.n_frames if 'n_frames' in img.__dict__ else 1
        if which('identify'):
            self.run_identify(img)
        else:
            getLogger('ocrd_exif').warning("ImageMagick 'identify' not available, Consider installing ImageMagick for more robust pixel density estimation")
            self.run_pil(img)

    def run_identify(self, img):
        for prop in ['compression', 'photometric_interpretation']:
            setattr(self, prop, img.info[prop] if prop in img.info else None)
        if img.filename:
            ret = run(['identify', '-format', r'%[resolution.x] %[resolution.y] %U', img.filename], check=False, stderr=PIPE, stdout=PIPE)
        else:
            with BytesIO() as bio:
                img.save(bio, format=img.format)
                ret = run(['identify', '-format', r'%[resolution.x] %[resolution.y] %U', '/dev/stdin'], check=False, stderr=PIPE, stdout=PIPE, input=bio.getvalue())
        if ret.returncode:
            stderr = ret.stderr.decode('utf-8')
            if 'no decode delegate for this image format' in stderr:
                getLogger('ocrd_exif').warning("ImageMagick does not support the '%s' image format. ", img.format)
            else:
                getLogger('ocrd_exif').error("identify exited with non-zero %s: %s", ret.returncode, stderr)
            self.xResolution = self.yResolution = 1
            self.resolutionUnit = 'inches'
        else:
            tokens = ret.stdout.decode('utf-8').split(' ', 3)
            self.xResolution = max(int(float(tokens[0])), 1)
            self.yResolution = max(int(float(tokens[1])), 1)
            self.resolutionUnit = 'inches' if tokens[2] == 'undefined' else \
                                  'cm' if tokens[2] == 'PixelsPerCentimeter' else \
                                  'inches'
        self.resolution = round(sqrt(self.xResolution * self.yResolution))

    def run_pil(self, img):
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
        Serialize all properties as XML string.
        """
        ret = '<exif>'
        for k in self.__dict__:
            ret += '<%s>%s</%s>' % (k, self.__dict__[k], k)
        ret += '</exif>'
        return ret
