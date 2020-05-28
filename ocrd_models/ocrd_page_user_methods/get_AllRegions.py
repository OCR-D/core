def get_AllRegions(self, classes=None, order='document'):
    """
    Get all the *Region element or only those provided by ``classes``.
    Returned in random order unless ``reading_order`` is set (NOT CURRENTLY IMPLEMENTED)
    Arguments:
        classes (list) Classes of regions that shall be returned, e.g. ['Text', 'Image']
        order ("document"|"reading-order") Whether to return regions sorted by document order (default) or by reading order
    """
    if order not in ['document', 'reading-order']:
        raise Exception("Argument 'order' must be either 'document' or 'reading-order', not '{}'".format(order))
    def region_class(x):
        return x.__class__.__name__.replace('RegionType', '')
    def get_recursive_regions(regions, level):
        if level == 1:
            # stop recursion, filter classes
            if classes:
                return [r for r in regions if region_class(r) in classes]
            else:
                return regions
        # find more regions recursively
        more_regions = []
        for region in regions:
            more_regions.append([])
            for class_ in ['Advert', 'Chart', 'Chem', 'Custom', 'Graphic', 'Image', 'LineDrawing', 'Map', 'Maths', 'Music', 'Noise', 'Separator', 'Table', 'Text', 'Unknown']:
                if class_ == 'Map' and not isinstance(region, PageType):
                    # 'Map' is not recursive in 2019 schema
                    continue
                 more_regions[-1] += getattr(region, 'get_{}Region'.format(class_))()
        if not any(more_regions):
            return get_recursive_regions(regions, 1)
        regions = [region for r, more in zip(regions, more_regions) for region in [r] + more]
        return get_recursive_regions(regions, level - 1 if level else 0)
    ret = get_recursive_regions([self], depth + 1 if depth else 0)
    if order == 'reading-order':
        reading_order = self.get_ReadingOrder()
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
            id2region = dict([(region.id, region) for region in ret])
            ret = [id2region[region_id] for region_id in reading_order if region_id in id2region]
    return ret
