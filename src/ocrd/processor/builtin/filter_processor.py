# pylint: disable=missing-module-docstring,invalid-name
from typing import Optional

from lxml import etree
import elementpath
import click

from ocrd import Processor, OcrdPageResult, OcrdPageResultImage
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_models.ocrd_file import OcrdFileType
from ocrd_models.ocrd_page import OcrdPage, to_xml
from ocrd_models.constants import NAMESPACES
from ocrd_utils import (
    make_file_id,
    MIME_TO_EXT,
    MIMETYPE_PAGE,
    xywh_from_points,
    parse_json_string_with_comments,
    resource_string,
    config
)
from ocrd_modelfactory import page_from_file

PARSER = elementpath.XPath2Parser(namespaces={**NAMESPACES, 'pc': NAMESPACES['page']})

def xpath(func, *, ns_uri: Optional[str] = None, ns_prefix: Optional[str] = ''):
    name = func.__name__.replace('_', '-')
    if ns_prefix and name.startswith(ns_prefix):
        name = name[len(ns_prefix):]
        if name.startswith('-'):
            name = name[1:]
    # register
    PARSER.external_function(func, name=name, prefix=ns_prefix)
    return func

def pc_xpath(func):
    return xpath(func, ns_uri=NAMESPACES['page'], ns_prefix='pc')

@pc_xpath
def pc_pixelarea(nodes):
    """
    Extract Coords/@points from all nodes, calculate the bounding
    box, and accumulate areas.
    """
    area = 0
    for node in nodes:
        # FIXME: find out why we need to go to the parent here
        node = node.parent.value
        coords = node.find(f'{node.prefix}:Coords', node.nsmap)
        if coords is None:
            continue
        points = coords.attrib['points']
        xywh = xywh_from_points(points)
        area += xywh['w'] * xywh['h']
    return area

@pc_xpath
def pc_textequiv(nodes):
    """
    Extract TextEquiv/Unicode from all nodes, then concatenate
    (interspersed with spaces or newlines).
    """
    text = ''
    for node in nodes:
        # FIXME: find out why we need to go to the parent here
        node = node.parent.value
        if text and node.tag.endswith('Region'):
            text += '\n'
        if text and node.tag.endswith('Line'):
            text += '\n'
        if text and node.tag.endswith('Word'):
            text += ' '
        equiv = node.find(f'{node.prefix}:TextEquiv', node.nsmap)
        if equiv is None:
            continue
        string = equiv.find(f'{node.prefix}:Unicode', node.nsmap)
        if string is None:
            continue
        text += str(string.text)
    return text

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
    def setup(self):
        token = PARSER.parse(self.parameter['select'])
        def select(root):
            context = elementpath.XPathContext(root)
            return token.get_results(context)
        self.selectxpath = select

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
        nodes = [node.attrib['id'] for node in self.selectxpath(pcgts.etree) if 'id' in node.attrib]
        # get PAGE objects from matching etree nodes
        # FIXME: this should be easier (OcrdPage should have id lookup mechanism)
        regions = pcgts.get_Page().get_AllRegions()
        textregions = [region for region in regions if region.original_tagname_ == 'TextRegion']
        lines = [line for region in textregions for line in region.get_TextLine() or []]
        words = [word for line in lines for word in line.get_Word() or []]
        glyphs = [glyph for word in words for glyph in word.get_Glyph() or []]
        segments = [segment for segment in regions + lines + words + glyphs
                    if segment.id in nodes]
        if not(len(segments)):
            self.logger.info("no matches")
            return result
        rodict = pcgts.get_Page().get_ReadingOrderGroups()
        if self.parameter['plot']:
            page_image, page_coords, _ = self.workspace.image_from_page(pcgts.get_Page(), page_id)
        for segment in segments:
            node = pcgts.mapping[id(segment)]
            assert isinstance(node, etree._Element)
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
