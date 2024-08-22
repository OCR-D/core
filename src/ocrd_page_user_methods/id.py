@property
def id(self):
    from ocrd_utils import make_xml_id
    if hasattr(self, 'pcGtsId'):
        return self.pcGtsId or ''
    return make_xml_id(self.imageFilename)
