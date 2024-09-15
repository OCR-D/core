# pylint: disable=missing-module-docstring,invalid-name
from typing import Optional

from lxml import etree
import click

from ocrd import Processor, OcrdPageResult, OcrdPageResultImage
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_models import OcrdPage

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

class FilterProcessor(Processor):
    def process_page_pcgts(self, *input_pcgts: Optional[OcrdPage], page_id: Optional[str] = None) -> OcrdPageResult:
        """
        Remove PAGE segment hierarchy elements based on flexible selection criteria.

        Open and deserialise PAGE input file, then iterate over the segment hierarchy
        down to the level required for ``select`` (which could be multiple levels at once).

        Remove any segments matching XPath query ``select`` from that hierarchy (and from
        the `ReadingOrder` if it is a region type).

        \b
        Besides full XPath 2.0 syntax, this supports extra predicates:
        - `pc:pixelarea()` for the number of pixels of the bounding box (or sum area on node sets),
        - `pc:textequiv()` for the first TextEquiv unicode string (or concatenated string on node sets).

        If ``plot`` is `true`, then extract and write an image file for all removed segments
        to the output fileGrp (without reference to the PAGE).

        Produce a new PAGE output file by serialising the resulting hierarchy.
        """
        pcgts = input_pcgts[0]
        result = OcrdPageResult(pcgts)
        nodes = pcgts.xpath(self.parameter['select'])
        # get PAGE objects from matching etree nodes
        # but allow only hierarchy segments
        segments = [segment for segment in map(pcgts.revmap.get, nodes)
                    if segment.__class__.__name__.replace('Type', '') in _SEGTYPES]
        if not(len(segments)):
            self.logger.info("no matches")
            return result
        rodict = pcgts.get_Page().get_ReadingOrderGroups()
        if self.parameter['plot']:
            page_image, page_coords, _ = self.workspace.image_from_page(pcgts.get_Page(), page_id)
        for segment in segments:
            segtype = segment.original_tagname_
            self.logger.info("matched %s segment %s", segtype, segment.id)
            parent = segment.parent_object_
            partype = parent.__class__.__name__.replace('Type', '')
            if partype == 'Page':
                getattr(parent, 'get_' + segtype)().remove(segment)
            elif partype.endswith('Region'):
                if segtype.endswith('Region'):
                    getattr(parent, 'get_' + segtype)().remove(segment)
                else:
                    parent.TextLine.remove(segment)
            elif partype == 'TextLine':
                parent.Word.remove(segment)
            elif partype == 'Word':
                parent.Glyph.remove(segment)
            else:
                raise Exception(f"unexpected type ({partype}) of parent for matched segment ({segtype})")
            segment.parent_object_ = None
            if segtype.endswith('Region') and segment.id in rodict:
                # remove from ReadingOrder as well
                roelem = rodict[segment.id]
                rorefs = getattr(roelem.parent_object_, roelem.__class__.__name__.replace('Type', ''))
                rorefs.remove(roelem)
                roelem.parent_object_ = None
                del rodict[segment.id]
            if self.parameter['plot']:
                segment_image, _ = self.workspace.image_from_segment(segment, page_image, page_coords)
                result.images.append(OcrdPageResultImage(segment_image, segment.id + '.IMG', None))
        return result

    @property
    def metadata_filename(self):
        return 'processor/builtin/dummy/ocrd-tool.json'

    @property
    def executable(self):
        return 'ocrd-filter'

@click.command()
@ocrd_cli_options
def cli(*args, **kwargs):
    return ocrd_cli_wrap_processor(FilterProcessor, *args, **kwargs)
