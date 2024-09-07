def get_ReadingOrderGroups(self) -> dict:
    """
    Aggregate recursive ReadingOrder into a dictionary, mapping each regionRef
    (i.e. segment `@id`) to its referring group object (i.e one of

    \b
    - :py:class:`.RegionRefType`
    - :py:class:`.RegionRefIndexedType`
    - :py:class:`.OrderedGroupType`
    - :py:class:`.OrderedGroupIndexedType`
    - :py:class:`.UnoderedGroupType`
    - :py:class:`.UnoderedGroupIndexedType`
    """
    def get_groupdict(group):
        regionrefs = list()
        if isinstance(group, (OrderedGroupType, OrderedGroupIndexedType)):
            regionrefs = (group.get_RegionRefIndexed() +
                          group.get_OrderedGroupIndexed() +
                          group.get_UnorderedGroupIndexed())
        if isinstance(group, (UnorderedGroupType, UnorderedGroupIndexedType)):
            regionrefs = (group.get_RegionRef() +
                          group.get_OrderedGroup() +
                          group.get_UnorderedGroup())
        refdict = {}
        for elem in regionrefs:
            refdict[elem.get_regionRef()] = elem
            if not isinstance(elem, (RegionRefType, RegionRefIndexedType)):
                refdict = {**refdict, **get_groupdict(elem)}
        return refdict
    ro = self.get_ReadingOrder()
    if ro is None:
        return {}
    return get_groupdict(ro.get_OrderedGroup() or ro.get_UnorderedGroup())
