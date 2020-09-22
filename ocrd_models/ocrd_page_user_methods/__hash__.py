def __hash__(self):
    if hasattr(self, 'pcGtsId'):
        val = self.pcGtsId
    elif hasattr(self, 'imageFilename'):
        val = self.imageFilename
    elif hasattr(self, 'id'):
        val = self.id
    else:
        raise ValueError("Cannot hash %s" % self)
    return hash(val)
