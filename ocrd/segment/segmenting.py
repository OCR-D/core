# -*- coding: utf-8 -*-
from __future__ import absolute_import

import exiftool

from lxml import etree as ET

from ocrd import init

class Segmenter:
    """
    Segments a page.
    """

    def __init__(self):
        """
        The constructor.
        """

        self.clear()

    def clear(self):
        """
        Resets the Segmenter.
        """

        self.handle = init.Handle()

    def set_handle(self, handle):
        """
        (Re)sets the internal handle.
        """
        self.handle = handle

    def segement(self):
        """
        Performs the segmentation.
        """
        pass
