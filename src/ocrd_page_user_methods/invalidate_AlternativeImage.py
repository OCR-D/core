def invalidate_AlternativeImage(self, feature_selector=None):
    """
    Remove derived images from this segment (due to changed coordinates).

    If `feature_selector` is not none, remove only images with
    matching ``@comments``, e.g. ``feature_selector=cropped,deskewed``.
    """
    existing_images = self.AlternativeImage or []
    removed_images = []
    if feature_selector:
        new_images = []
        for image in existing_images:
            features = image.get_comments() or ''
            if any(feature in features.split(',')
                   for feature in feature_selector.split(',') if feature):
                removed_images.append(image)
            else:
                new_images.append(image)
        self.AlternativeImage = new_images
    else:
        removed_images = existing_images
        self.AlternativeImage = []
    if hasattr(self, 'id'):
        name = self.id
    elif hasattr(self, 'parent_object_') and hasattr(self.parent_object_, 'pcGtsId'):
        name = self.parent_object_.pcGtsId
    else:
        name = ''
    for image in removed_images:
        self.gds_collector_.add_message('Removing AlternativeImage %s from "%s"' % (
            image.get_comments() or '', name))
