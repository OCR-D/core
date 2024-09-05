# pylint: disable=missing-module-docstring,invalid-name
from typing import Optional

from lxml import etree
import click

from ocrd import Processor, OcrdPageResult, OcrdPageResultImage
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_models.ocrd_file import OcrdFileType
from ocrd_models.ocrd_page import OcrdPage, to_xml
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

def pc_area(ctxt, node):
    # FIXME find out why this gets passed as list
    node = node[0]
    coords = node.find(f'{node.prefix}:Coords', node.nsmap)
    if coords is None:
        return 0
    points = coords.attrib['points']
    xywh = xywh_from_points(points)
    return xywh['w'] * xywh['h']

def pc_text(ctxt, node):
    # FIXME find out why this gets passed as list
    node = node[0]
    equiv = node.find(f'{node.prefix}:TextEquiv', node.nsmap)
    if equiv is None:
        return ''
    string = equiv.find(f'{node.prefix}:Unicode', node.nsmap)
    if string is None:
        return ''
    return string.text

class FilterProcessor(Processor):

    def setup(self):
        ns = etree.FunctionNamespace(None)
        ns['pixelarea'] = pc_area
        # cannot use text() - conflicts with builtin fn
        ns['textequiv'] = pc_text

    def process_page_pcgts(self, *input_pcgts: Optional[OcrdPage], page_id: Optional[str] = None) -> OcrdPageResult:
        """
        Remove segments based on flexible selection criteria.

        Open and deserialise PAGE input file, then iterate over the segment hierarchy
        down to the level required for ``type``.

        Remove any segments of type ``type`` which also evaluate the XPath predicate ``query``
        to true (or non-empty).

        If ``plot`` is `true`, then extract and write an image file for all removed segments
        to the output fileGrp (without reference to the PAGE).

        Produce a new PAGE output file by serialising the resulting hierarchy.
        """
        pcgts = input_pcgts[0]
        result = OcrdPageResult(pcgts)
        root = pcgts.etree
        NS = {'re': 'http://exslt.org/regular-expressions',
              'pc': root.nsmap[root.prefix],
              root.prefix: root.nsmap[root.prefix]}
        segtype = self.parameter['type']
        segpred = self.parameter['query']
        if segtype == 'region':
            segments = pcgts.get_Page().get_AllRegions()
        elif segtype == 'line':
            segments = pcgts.get_Page().get_AllTextLines()
        elif segtype == 'word':
            lines = pcgts.get_Page().get_AllTextLines()
            segments = [word for line in lines for word in line.get_Word() or []]
        elif segtype == 'glyph':
            lines = pcgts.get_Page().get_AllTextLines()
            segments = [glyph for line in lines for word in line.get_Word() or [] for glyph in word.get_Glyph() or []]
        else:
            nodes = [node.attrib['id'] for node in pcgts.etree.xpath(f'//pc:{segtype}', namespaces=NS)]
            regions = pcgts.get_Page().get_AllRegions()
            textregions = [region for region in regions if region.original_tagname_ == 'TextRegion']
            lines = [line for region in textregions for line in region.get_TextLine() or []]
            words = [word for line in lines for word in line.get_Word() or []]
            glyphs = [glyph for word in words for glyph in word.get_Glyph() or []]
            segments = [segment for segment in regions + lines + words + glyphs
                        if segment.id in nodes or segtype == 'all']
        if not(len(segments)):
            self.logger.info("no matches")
            return result
        if self.parameter['plot']:
            page_image, page_coords, _ = self.workspace.image_from_page(pcgts.get_Page(), page_id)
        for segment in segments:
            node = pcgts.mapping[id(segment)]
            if not segpred or node.xpath(segpred, namespaces=NS):
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
