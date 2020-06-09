# pylint: disable=line-too-long,invalid-name,missing-module-docstring
def sort_AllIndexed(self, validate_uniqueness=True):
    """
    Sort all indexed children in-place.
    """
    elements = self.get_AllIndexed(index_sort=True)
    self.clear_AllIndexed()
    for element in elements:
        if isinstance(element, RegionRefIndexedType): # pylint: disable=undefined-variable
            self.add_RegionRefIndexed(element)
        elif isinstance(element, OrderedGroupIndexedType): # pylint: disable=undefined-variable
            self.add_OrderedGroupIndexed(element)
        elif isinstance(element, UnorderedGroupIndexedType): # pylint: disable=undefined-variable
            self.add_UnorderedGroupIndexed(element)
    return self.get_AllIndexed()

