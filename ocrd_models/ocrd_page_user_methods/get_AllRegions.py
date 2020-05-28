# pylint: disable=line-too-long,invalid-name,protected-access,missing-module-docstring
def _region_class(self, x): # pylint: disable=unused-argument
    return x.__class__.__name__.replace('RegionType', '')

def _get_recursive_regions(self, regions, level, classes=None):
    if level == 1:
        # stop recursion, filter classes
        if classes:
            return [r for r in regions if self._region_class(r) in classes]
        # remove the first element (PageType)
        return regions[1:]
    # find more regions recursively
    more_regions = []
    for region in regions:
        more_regions.append([])
        for class_ in ['Advert', 'Chart', 'Chem', 'Custom', 'Graphic', 'Image',
                       'LineDrawing', 'Map', 'Maths', 'Music', 'Noise',
                       'Separator', 'Table', 'Text', 'Unknown']:
            if class_ == 'Map' and not isinstance(region, PageType): # pylint: disable=undefined-variable
                # 'Map' is not recursive in 2019 schema
                continue
            more_regions[-1] += getattr(region, 'get_{}Region'.format(class_))()
    if not any(more_regions):
        return _get_recursive_regions(regions, 1, classes)
    regions = [region for r, more in zip(regions, more_regions) for region in [r] + more]
    return self._get_recursive_regions(regions, level - 1 if level else 0, classes)

def _get_recursive_reading_order(self, rogroup):
    if isinstance(rogroup, (OrderedGroupType, OrderedGroupIndexedType)): # pylint: disable=undefined-variable
        elements = rogroup.get_AllIndexed()
    if isinstance(rogroup, (UnorderedGroupType, UnorderedGroupIndexedType)): # pylint: disable=undefined-variable
        elements = (rogroup.get_RegionRef() + rogroup.get_OrderedGroup() + rogroup.get_UnorderedGroup())
    regionrefs = list()
    for elem in elements:
        regionrefs.append(elem.get_regionRef())
        if not isinstance(elem, (RegionRefType, RegionRefIndexedType)): # pylint: disable=undefined-variable
            regionrefs.extend(self._get_recursive_reading_order(elem))
    return regionrefs

def get_AllRegions(self, classes=None, order='document', depth=1):
    """
    Get all the *Region element or only those provided by ``classes``.
    Returned in document order unless ``order`` is ``reading-order``
    Arguments:
        classes (list) Classes of regions that shall be returned, e.g. ``['Text', 'Image']``
        order ("document"|"reading-order") Whether to return regions sorted by document order (default) or by reading order
        depth (int) Recursive depth to look for regions at. Default: 1
    """
    if order not in ['document', 'reading-order']:
        raise Exception("Argument 'order' must be either 'document' or 'reading-order', not '{}'".format(order))
    ret = self._get_recursive_regions([self], depth + 1 if depth else 0, classes)
    if order == 'reading-order':
        reading_order = self.get_ReadingOrder()
        if reading_order:
            reading_order = reading_order.get_OrderedGroup() or reading_order.get_UnorderedGroup()
        if reading_order:
            reading_order = self._get_recursive_reading_order(reading_order)
        if reading_order:
            id2region = dict([(region.id, region) for region in ret]) # pylint: disable=consider-using-dict-comprehension
            ret = [id2region[region_id] for region_id in reading_order if region_id in id2region]
    return ret
