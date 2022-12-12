def prune_ReadingOrder(self):
    """
    Remove any empty ReadingOrder elements
    """
    ro = self.get_Page().get_ReadingOrder()
    if ro:
        og = ro.get_OrderedGroup()
        if og and (not og.get_RegionRefIndexed() and
                   not og.get_OrderedGroupIndexed() and
                   not og.get_UnorderedGroupIndexed()):
            og = None
        ug = ro.get_UnorderedGroup()
        if ug and (not ug.get_RegionRef() and
                   not ug.get_OrderedGroup() and
                   not ug.get_UnorderedGroup()):
            ug = None
        if not og and not ug:
            self.get_Page().set_ReadingOrder(None)
