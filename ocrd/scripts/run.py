from __future__ import absolute_import

import click,os

import xml.dom.minidom as md

from lxml import etree as ET

from ocrd import init, characterize, segment, recognize

@click.command()
@click.option('-w', '--working-dir', default='/tmp', help='Path to store intermediate and result files (default: "/tmp")', type=click.Path(exists=True))
@click.option('-m', '--model', required=True, help='OCR model to load', type=click.File('r'))
@click.argument('METS_XML', type=click.File('rb'))
def cli(working_dir, model, mets_xml):
    """
    Perform OCR for a given METS file.
    """

    # read METS
    initializer = init.Initializer()
    initializer.load(mets_xml)

    # set the working dir
    initializer.set_working_dir(working_dir)

    # initialize
    initializer.initialize()

    # image characterization
    characterizer = characterize.Characterizer()
    characterizer.set_handle(initializer.get_handle())
    characterizer.characterize()

    # page segmentation
    page_segmenter = segment.PageSegmenter()
    page_segmenter.set_handle(initializer.get_handle())
    page_segmenter.segment()

    # region segmentation
    region_segmenter = segment.RegionSegmenter()
    region_segmenter.set_handle(initializer.get_handle())
    region_segmenter.segment()

    # text recognition
    recognizer = recognize.Recognizer()
    recognizer.set_handle(initializer.get_handle())
    recognizer.set_model(path=os.path.dirname(model.name),model=os.path.splitext(os.path.basename(model.name))[0])
    recognizer.recognize()

    # output
    for ID in initializer.get_handle().page_trees:
        print(md.parseString(ET.tostring(initializer.get_handle().page_trees[ID].getroot(), encoding='utf8', method='xml')).toprettyxml(indent="\t"))
        pass
