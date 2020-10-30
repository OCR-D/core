def set_Coords(self, Coords):
    """
    Set coordinate polygon by given object.
    Moreover, invalidate self's AlternativeImages
    (because they will have been cropped with a bbox
     of the previous polygon).
    """
    if hasattr(self, 'invalidate_AlternativeImage'):
        # RegionType, TextLineType, WordType, GlyphType:
        self.invalidate_AlternativeImage()
    elif hasattr(self, 'parent_object_') and hasattr(self.parent_object_, 'invalidate_AlternativeImage'):
        # BorderType:
        self.parent_object_.invalidate_AlternativeImage(feature_selector='cropped')
    self.Coords = Coords
