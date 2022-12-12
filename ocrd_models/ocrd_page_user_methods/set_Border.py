def set_Border(self, Border):
    """
    Set coordinate polygon by given :py:class:`BorderType` object.
    Moreover, invalidate self's ``pc:AlternativeImage``s
    (because they will have been cropped with a bbox
    of the previous polygon).
    """
    self.invalidate_AlternativeImage(feature_selector='cropped')
    self.Border = Border
