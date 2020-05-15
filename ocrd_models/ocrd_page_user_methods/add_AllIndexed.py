def add_AllIndexed(self, elements):
    if not isinstance(elements, list):
        elements = [elements]
    for element in sorted(elements, key=lambda x : x.index):
        if isinstance(element, RegionRefIndexedType):
            self.add_RegionRefIndexed(element)
        elif isinstance(element, OrderedGroupIndexedType):
            self.add_OrderedGroupIndexed(element)
        elif isinstance(element, UnorderedGroupIndexedType):
            self.add_UnorderedGroupIndexed(element)
    return self.get_AllIndexed()

