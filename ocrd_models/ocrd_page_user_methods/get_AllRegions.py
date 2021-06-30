# pylint: disable=line-too-long,invalid-name,protected-access,missing-module-docstring
def _region_class(self, x): # pylint: disable=unused-argument
    return x.__class__.__name__.replace('RegionType', '')

def _get_recursive_regions(self, regions, level, classes=None):
    from .constants import PAGE_REGION_TYPES  # pylint: disable=relative-beyond-top-level,import-outside-toplevel
    if level == 1:
        # stop recursion, filter classes
        if classes:
            return [r for r in regions if self._region_class(r) in classes]
        if regions and regions[0].__class__.__name__ == 'PageType':
            regions = regions[1:]
        return regions
    # find more regions recursively
    more_regions = []
    for region in regions:
        more_regions.append([])
        for class_ in PAGE_REGION_TYPES:
            if class_ == 'Map' and not isinstance(region, PageType): # pylint: disable=undefined-variable
                # 'Map' is not recursive in 2019 schema
                continue
            more_regions[-1] += getattr(region, 'get_{}Region'.format(class_))()
    if not any(more_regions):
        return self._get_recursive_regions(regions, 1, classes)
    ret = []
    for r, more in zip(regions, more_regions):
        ret.append(r)
        ret += self._get_recursive_regions(more, level - 1 if level else 0, classes)
    return self._get_recursive_regions(ret, 1, classes)

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

def get_AllRegions(self, classes=None, order='document', depth=0):
    """
    Get all the ``*Region`` elements, or only those provided by `classes`.
    Return in document order, unless `order` is ``reading-order``.

    Arguments:
        classes (list): Classes of regions that shall be returned, \
            e.g. ``['Text', 'Image']``
        order ("document"|"reading-order"|"reading-order-only"): Whether to \
            return regions sorted by document order (``document``, default) or by
            reading order with regions not in the reading order at the end of the
            returned list (``reading-order``) or regions not in the reading order
            omitted (``reading-order-only``)
        depth (int): Recursive depth to look for regions at, set to `0` for \
            all regions at any depth. Default: 0

    Returns:
        a list of :py:class:`TextRegionType`, :py:class:`ImageRegionType`, \
            :py:class:`LineDrawingRegionType`, :py:class:`GraphicRegionType`, \
            :py:class:`TableRegionType`, :py:class:`ChartRegionType`, \
            :py:class:`MapRegionType`, :py:class:`SeparatorRegionType`, \
            :py:class:`MathsRegionType`, :py:class:`ChemRegionType`, \
            :py:class:`MusicRegionType`, :py:class:`AdvertRegionType`, \
            :py:class:`NoiseRegionType`, :py:class:`UnknownRegionType`, \
            and/or :py:class:`CustomRegionType`

    For example, to get all text anywhere on the page in reading order, use:
    ::
        '\\n'.join(line.get_TextEquiv()[0].Unicode
                  for region in page.get_AllRegions(classes=['Text'], depth=0, order='reading-order')
                  for line in region.get_TextLine())
    """
    if order not in ['document', 'reading-order', 'reading-order-only']:
        raise Exception("Argument 'order' must be either 'document', 'reading-order' or 'reading-order-only', not '{}'".format(order))
    if depth < 0:
        raise Exception("Argument 'depth' must be an integer greater-or-equal 0, not '{}'".format(depth))
    ret = self._get_recursive_regions([self], depth + 1 if depth else 0, classes)
    if order.startswith('reading-order'):
        reading_order = self.get_ReadingOrder()
        if reading_order:
            reading_order = reading_order.get_OrderedGroup() or reading_order.get_UnorderedGroup()
        if reading_order:
            reading_order = self._get_recursive_reading_order(reading_order)
        if reading_order:
            id2region = {region.id: region for region in ret}
            in_reading_order = [id2region[region_id] for region_id in reading_order if region_id in id2region]
            #  print("ret: {} / in_ro: {} / not-in-ro: {}".format(
            #      len(ret),
            #      len([id2region[region_id] for region_id in reading_order if region_id in id2region]),
            #      len([r for r in ret if r not in in_reading_order])
            #      ))
            if order == 'reading-order-only':
                ret = in_reading_order
            else:
                ret = in_reading_order + [r for r in ret if r not in in_reading_order]
    return ret
