@property
def id(self):
    if hasattr(self, 'pcGtsId'):
        return self.pcGtsId or ''
    return self.imageFilename
