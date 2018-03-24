import logging
logging.basicConfig(level=logging.DEBUG)

def getLogger(*args, **kwargs):
    return logging.getLogger(*args, **kwargs)

def coordinate_string_from_xywh(box):
    """
    Constructs a polygon representation from a rectangle described as a dict with keys x, y, w, h.
    """
    # tesseract uses a different region representation format
    return "%i,%i %i,%i %i,%i %i,%i" % (
        box['x'],
        box['y'],
        box['x'] + box['w'],
        box['y'] + box['w'],
        box['x'] + box['w'] + box['h'],
        box['y'] + box['w'] + box['h'],
        box['x'] + box['h'],
        box['y'] + box['h']
    )

def xywh_from_coordinate_string(points):
    """
    Constructs a numpy-compatible polygon from a page representation.
    """
    polygon = []
    for pair in points.split(" "):
        x_y = pair.split(",")
        polygon.append([float(x_y[0]), float(x_y[1])])
    return polygon
