# pylint: disable=line-too-long,invalid-name,missing-module-docstring
def extend_AllIndexed(self, elements, validate_continuity=False):
    """
    Add all elements in list `elements`, respecting ``@index`` order.
    With `validate_continuity`, check that all new elements come after all old elements
    (or raise an exception). 
    Otherwise, ensure this condition silently (by increasing ``@index`` accordingly).
    """
    if not isinstance(elements, list):
        elements = [elements]
    siblings = self.get_AllIndexed()
    highest_sibling_index = siblings[-1].index if siblings else -1
    if validate_continuity:
        elements = sorted(elements, key=lambda x: x.index)
        lowest_element_index = elements[0].index
        if lowest_element_index <= highest_sibling_index:
            raise Exception("@index already used: {}".format(lowest_element_index))
    else:
        for element in elements:
            highest_sibling_index += 1
            element.index = highest_sibling_index
    for element in elements:
        if isinstance(element, RegionRefIndexedType): # pylint: disable=undefined-variable
            self.add_RegionRefIndexed(element)
        elif isinstance(element, OrderedGroupIndexedType): # pylint: disable=undefined-variable
            self.add_OrderedGroupIndexed(element)
        elif isinstance(element, UnorderedGroupIndexedType): # pylint: disable=undefined-variable
            self.add_UnorderedGroupIndexed(element)
    return self.get_AllIndexed()
