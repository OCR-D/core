def set_points(self, points):
    """
    Set coordinate polygon by given string.
    Moreover, invalidate the parent's ``pc:AlternativeImage``s
    (because they will have been cropped with a bbox
    of the previous polygon).
    """
    if hasattr(self, 'parent_object_'):
        parent = self.parent_object_
        if hasattr(parent, 'invalidate_AlternativeImage'):
            # RegionType, TextLineType, WordType, GlyphType:
            parent.invalidate_AlternativeImage()
        elif hasattr(parent, 'parent_object_') and hasattr(parent.parent_object_, 'invalidate_AlternativeImage'):
            # BorderType:
            parent.parent_object_.invalidate_AlternativeImage(feature_selector='cropped')
    self.points = points
