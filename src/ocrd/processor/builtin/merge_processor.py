# pylint: disable=missing-module-docstring,invalid-name
from typing import Optional
from itertools import count
from collections import OrderedDict as odict

import click

from ocrd import Processor, OcrdPageResult
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_modelfactory import page_from_file
from ocrd_models import OcrdPage
from ocrd_models.ocrd_page import (
    BorderType,
    CoordsType,
    ReadingOrderType,
    UnorderedGroupType,
)
from ocrd_utils import bbox_from_points

_SEGTYPES = [
    "NoiseRegion",
    "LineDrawingRegion",
    "AdvertRegion",
    "ImageRegion",
    "ChartRegion",
    "MusicRegion",
    "GraphicRegion",
    "UnknownRegion",
    "CustomRegion",
    "SeparatorRegion",
    "MathsRegion",
    "TextRegion",
    "MapRegion",
    "ChemRegion",
    "TableRegion",
    "TextLine",
    "Word",
    "Glyph"
]


def get_border_bbox(pcgts):
    if pcgts.Page.Border is None:
        return [0, 0, pcgts.Page.imageWidth, pcgts.Page.imageHeight]
    return bbox_from_points(pcgts.Page.Border.Coords.points)

def rename_segments(pcgts, start=1):
    renamed = {}
    rodict = pcgts.Page.get_ReadingOrderGroups()
    # get everything that has an identifier
    nodes = pcgts.xpath("//*[@id]")
    # filter segments
    segments = [segment for segment in map(pcgts.revmap.get, nodes)
                # get PAGE objects from matching etree nodes
                # but allow only hierarchy segments
                if segment.__class__.__name__.replace('Type', '') in _SEGTYPES]
    # count segments and rename them
    # fixme: or perhaps better to have each segment type named and counted differently?
    num = 0
    regions = []
    for num, segment in zip(count(start=start), segments):
        segtype = segment.original_tagname_
        #parent = segment.parent_object_
        newname = "seg%011d" % num
        assert not segment.id in renamed
        if segtype.endswith('Region') and segment.id in rodict:
            # update reading order
            roelem = rodict[segment.id]
            roelem.regionRef = newname
        renamed[segment.id] = newname
        segment.id = newname
    return num

class MergeProcessor(Processor):
    def process_page_pcgts(self, *input_pcgts: Optional[OcrdPage], page_id: Optional[str] = None) -> OcrdPageResult:
        """
        Merge PAGE segment hierarchy elements from all input file groups.

        For each page, open and deserialise PAGE input files. Rename all elements
        of the segment hierarchy to new (clash-free) identifers. Redefine the
        `Border` coordinates as the convex hull of all input borders. Then add all
        regions from all input files, concatenating them into a single `ReadingOrder`
        in the order of input file groups.

        Produce a new PAGE output file by serialising the resulting hierarchy.
        """
        actual_pcgts = list(filter(None, input_pcgts))
        assert len(set(pcgts.Page.imageFilename for pcgts in actual_pcgts)) == 1, \
            "input files must all reference the same @imageFilename"
        # create new PAGE for image
        result = OcrdPageResult(page_from_file(actual_pcgts[0].Page.imageFilename))
        # unify Border
        borders = [get_border_bbox(pcgts) for pcgts in actual_pcgts]
        minx, miny, maxx, maxy = zip(*borders)
        minx = min(minx)
        miny = min(miny)
        maxx = max(maxx)
        maxy = max(maxy)
        result.pcgts.Page.set_Border(
            BorderType(CoordsType(
                points=f"{minx},{miny} {maxx},{miny} {maxx},{maxy} {minx},{maxy}")))
        # rename all segments
        num = 1
        for pcgts in actual_pcgts:
            num = rename_segments(pcgts, num)
        # concatenate all regions
        ug = UnorderedGroupType(id="merged")
        result.pcgts.Page.set_ReadingOrder(ReadingOrderType(UnorderedGroup=ug))
        for pcgts in actual_pcgts:
            for region in pcgts.Page.get_AllRegions():
                adder = getattr(result.pcgts.Page, 'add_' + region.original_tagname_)
                adder(region)
            if pcgts.Page.ReadingOrder:
                group = pcgts.Page.ReadingOrder.OrderedGroup or pcgts.Page.ReadingOrder.UnorderedGroup
                adder = getattr(ug, 'add_' + group.original_tagname_)
                adder(group)
        return result

    @property
    def metadata_filename(self):
        return 'processor/builtin/dummy/ocrd-tool.json'

    @property
    def executable(self):
        return 'ocrd-merge'


@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(MergeProcessor, *args, **kwargs)
