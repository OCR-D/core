# pylint: disable=line-too-long,invalid-name,missing-module-docstring,missing-function-docstring
def extend_AllIndexed(self, elements):
    if not isinstance(elements, list):
        elements = [elements]
    for element in sorted(elements, key=lambda x: x.index):
        if isinstance(element, RegionRefIndexedType): # pylint: disable=undefined-variable
            self.add_RegionRefIndexed(element)
        elif isinstance(element, OrderedGroupIndexedType): # pylint: disable=undefined-variable
            self.add_OrderedGroupIndexed(element)
        elif isinstance(element, UnorderedGroupIndexedType): # pylint: disable=undefined-variable
            self.add_UnorderedGroupIndexed(element)
    return self.get_AllIndexed()

