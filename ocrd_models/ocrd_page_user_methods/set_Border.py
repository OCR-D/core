def set_Border(self, Border):
    """
    Set coordinate polygon by given object.
    Moreover, invalidate self's AlternativeImages
    (because they will have been cropped with a bbox
     of the previous polygon).
    """
    self.invalidate_AlternativeImage(feature_selector='cropped')
    self.Border = Border
