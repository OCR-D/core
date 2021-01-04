def get_AllTextLines(self):
    """
    Return all the TextLine in the document
    """
    ret = []
    for reg in self.get_AllRegions(['Text']):
        ret += reg.get_TextLine()
    return ret

