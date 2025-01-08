from ocrd_utils import xywh_from_points

pc_functions = []

def _export(func):
    pc_functions.append(func)
    return func

@_export
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

@_export
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

