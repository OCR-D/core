"""
Utilities for ocrd_models
"""
from lxml import etree as ET

__all__ = [
    'xmllint_format',
]

def xmllint_format(xml):
    """
    Pretty-print XML like ``xmllint`` does.

    Arguments:
        xml (string): Serialized XML
    """
    parser = ET.XMLParser(resolve_entities=False, strip_cdata=False, remove_blank_text=True)
    document = ET.fromstring(xml, parser)
    return ('%s\n%s' % ('<?xml version="1.0" encoding="UTF-8"?>',
                        ET.tostring(document, pretty_print=True, encoding='UTF-8').decode('utf-8'))).encode('utf-8')
