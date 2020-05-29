# pylint: disable=line-too-long,invalid-name,missing-module-docstring
def extend_AllIndexed(self, elements):
    """
    Add all elements in list ``elements``, respecting ``@index`` order.
    """
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

