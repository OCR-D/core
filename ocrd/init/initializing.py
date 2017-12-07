# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

class Initializer:

    def __init__(self):
        """
        The constructor.
        """

        self.clear()

    def clear(self):
        """
        Resets the Initializer.
        """

        self.tree = ET.ElementTree()
        self.set_working_dir("./")

    def set_working_dir(self,path):
        """
        (Re)sets the working directory.
        """
        self.working_dir = path

    def load_string(self,mets_xml):
        """
        Loads METS XML from a string.
        """
        pass

    def load(self,mets_xml_file):
        """
        Loads METS XML from a file (i.e. file name).
        """
        self.tree.parse(mets_xml_file)

    def initialize(self):
        """
        Performs the initialization.

        Image files are crawled and copied to the WD.
        PAGE XML files are either crawled or created and copied to the WD.
        """

        self._load_and_create_page()


    def _load_and_create_page(self):
        """
        Loads and creates missing PAGE XML from internal METS tree.
        """
        pass
