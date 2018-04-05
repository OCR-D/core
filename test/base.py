import os
import sys

from unittest import TestCase, skip, main # pylint: disable=unused-import

PWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PWD + '/../ocrd')

class Assets(object):

    def __init__(self, baseurl=None):
        if baseurl is None:
            baseurl = 'file://' + PWD + '/assets/'
        self.baseurl = baseurl

    def url_of(self, path, baseurl=None):
        if baseurl is None:
            baseurl = self.baseurl
        return self.baseurl + path


_baseurl = None
if 'OCRD_BASEURL' in os.environ:
    _baseurl = os.environ['OCRD_BASEURL']
assets = Assets(baseurl=_baseurl)
