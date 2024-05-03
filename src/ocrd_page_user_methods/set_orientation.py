def set_orientation(self, orientation):
    """
    Set deskewing angle to given `orientation` number.
    Moreover, invalidate self's ``pc:AlternativeImage``s
    (because they will have been rotated and enlarged
    with the angle of the previous value).
    """
    if hasattr(self, 'invalidate_AlternativeImage'):
        # PageType, RegionType:
        self.invalidate_AlternativeImage(feature_selector='deskewed')
    self.orientation = orientation
