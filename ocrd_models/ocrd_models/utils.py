"""
Utilities for ocrd_models
"""
from lxml import etree as ET

from ocrd_utils import getLogger
from .constants import NAMESPACES as NS

__all__ = [
    'xmllint_format',
    'handle_oai_response',
    'is_oai_content',
    'extract_mets_from_oai_content'
]

def xmllint_format(xml):
    """
    Pretty-print XML like ``xmllint`` does.

    Arguments:
        xml (string): Serialized XML
    """
    log = getLogger('ocrd_models.utils.xmllint_format')
    parser = ET.XMLParser(resolve_entities=False, strip_cdata=False, remove_blank_text=True)
    document = ET.fromstring(xml, parser)
    return ('%s\n%s' % ('<?xml version="1.0" encoding="UTF-8"?>',
                        ET.tostring(document, pretty_print=True, encoding='UTF-8').decode('utf-8'))).encode('utf-8')

def handle_oai_response(response):
    """
    In case of a valid OAI-Response, extract first METS-Entry-Data
    """
    log = getLogger('ocrd_models.utils.handle_oai_response')
    content_type = response.headers['Content-Type']
    if 'xml' in content_type or 'text' in content_type:
        content = response.content
        try:
            if is_oai_content(content):
                return extract_mets_from_oai_content(content)
        except ET.LxmlError as exc:
            log.warning("textual response but no xml: %s (%s)", content, exc)
    return response.content


def is_oai_content(data):
    """
    Return True if data is an OAI-PMH request/response
    """
    log = getLogger('ocrd_models.utils.is_oai_content')
    xml_root = ET.fromstring(data)
    root_tag = xml_root.tag
    log.info("response data root.tag: '%s'" % root_tag)
    return str(root_tag).endswith('OAI-PMH')


def extract_mets_from_oai_content(data, preamble='<?xml version="1.0" encoding="UTF-8"?>'):
    """
    Extract METS from an OAI-PMH GetRecord response
    """
    xml_root = ET.fromstring(data)
    if 'mets' in xml_root.tag:
        return data
    mets_root_el = xml_root.find('.//{%s}mets' % NS['mets'])
    if mets_root_el is not None:
        new_tree = ET.ElementTree(mets_root_el)
        xml_formatted = ET.tostring(new_tree,
                                pretty_print=True,
                                encoding='UTF-8').decode('UTF-8')
        formatted_content = '{}\n{}'.format(preamble, xml_formatted)
        return formatted_content.encode('UTF-8').replace(b'\n', b'\r\n')

    raise Exception("Missing mets-section in %s" % data)
