# -*- coding: utf-8 -*-

import os
import requests

from lxml import etree as ET

ns = { 'mets'  : "http://www.loc.gov/METS/",
       'mods'  : "http://www.loc.gov/mods/v3",
       'xlink' : "http://www.w3.org/1999/xlink",
     }

class Handle:
    """
    Internal data structure.
    """

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
        self.img_src = {}
        self.img_files = {}
        self.page_src = {}
        self.page_files = {}
        self.page_trees = {}

class Initializer:
    """
    Initializes an OCR process given a METS XML file.
    """

    def __init__(self):
        """
        The constructor.
        """

        self.clear()

    def clear(self):
        """
        Resets the Initializer.
        """

        self.set_working_dir("./")
        self.handle = Handle()

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
        self.handle.tree.parse(mets_xml_file)

    def initialize(self):
        """
        Performs the initialization.

        Image files are crawled and copied to the WD.
        PAGE XML files are either crawled or created and copied to the WD.
        """

        self._load_images()
        self._load_or_create_page()


    def _load_or_create_page(self):
        """
        Loads or creates missing PAGE XML from internal METS tree.
        """
        page_fileGrps = self.handle.tree.getroot().findall(".//mets:fileGrp[@USE='FULLTEXT']", ns)
        # case load page
        if page_fileGrps:
            for page_fileGrp in page_fileGrps:
                page_files = page_fileGrp.findall("./mets:file", ns)
                for page_file in page_files:
                    # extract information from elem
                    page_ID = page_file.get("ID")
                    ID = page_ID.rstrip("_FULLTEXT")
                    page_url = page_file.find("mets:FLocat", ns).get("{%s}href" % ns["xlink"])

                    # make a local copy
                    page_data = requests.get(page_url)
                    if page_data.status_code == 200:
                        self.handle.page_src[ID] = page_url
                        self.handle.page_files[ID] = "%s/%s" % (self.working_dir, os.path.basename(page_url))
                        with open(self.handle.page_files[ID], 'wb') as f:  
                            f.write(page_data.content)
                        # parse the page xml (and store the tree to avoid repeated parsing)
                        self.handle.page_trees[ID] = ET.ElementTree()
                        self.handle.page_trees[ID].parse(self.handle.page_files[ID])
        # case create page TODO
        else:
            pass

    def _load_images(self):
        """
        Retrieves images referenced in the METS and copies them to the WD.
        """
        img_fileGrps = self.handle.tree.getroot().findall(".//mets:fileGrp[@USE='IMAGE']", ns)
        for img_fileGrp in img_fileGrps:
            img_files = img_fileGrp.findall("./mets:file", ns)
            for img_file in img_files:
                # extract information from elem
                img_ID = img_file.get("ID")
                ID = img_ID.rstrip("_IMAGE")
                img_url = img_file.find("mets:FLocat", ns).get("{%s}href" % ns["xlink"])

                # make a local copy
                img_data = requests.get(img_url)
                if img_data.status_code == 200:
                    self.handle.img_src[ID] = img_url
                    self.handle.img_files[ID] = "%s/%s" % (self.working_dir, os.path.basename(img_url))
                    with open(self.handle.img_files[ID], 'wb') as f:  
                        f.write(img_data.content)

    def get_handle(self):
        """
        Returns the internal handle.
        """
        return self.handle
