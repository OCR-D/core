def get_AllRegions(self, regions=None, reading_order=False):
    """"
    Get all the *Region element or only those provided by ``regions``.
    Returned in random order unless ``reading_order`` is set (NOT CURRENTLY IMPLEMENTED)
    """
    if reading_order:
        reading_order = self.get_ReadingOrder()
    if not regions:
        regions = ['Advert', 'Chart', 'Chem', 'Custom', 'Graphic', 'Image', 'LineDrawing', 'Map', 'Maths', 'Music', 'Noise', 'Separator', 'Table', 'Text', 'Unknown']
    ret = []
    for region in regions:
        ret += getattr(self, 'get_{}Region'.format(region))()
    if reading_order:
        reading_order = reading_order.get_OrderedGroup() or reading_order.get_UnorderedGroup()
    if reading_order:
        def get_recursive_reading_order(rogroup):
            if isinstance(rogroup, (OrderedGroupType, OrderedGroupIndexedType)):
                elements = rogroup.get_AllIndexed()
            if isinstance(rogroup, (UnorderedGroupType, UnorderedGroupIndexedType)):
                elements = (rogroup.get_RegionRef() + rogroup.get_OrderedGroup() + rogroup.get_UnorderedGroup())
            regionrefs = list()
            for elem in elements:
                regionrefs.append(elem.get_regionRef())
                if not isinstance(elem, (RegionRefType, RegionRefIndexedType)):
                    regionrefs.extend(get_recursive_reading_order(elem))
            return regionrefs
        reading_order = get_recursive_reading_order(reading_order)
    if reading_order:
        ret = dict([(region.id, region) for region in ret])
        ret = [ret[region_id] for region_id in reading_order if region_id in ret]
    ret = [r in ret if r.__class__.__name__.replace('RegionType', '') in regions
    return ret
