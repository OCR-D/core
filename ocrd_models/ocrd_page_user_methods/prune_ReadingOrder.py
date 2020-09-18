def prune_ReadingOrder(self):
    """
    Remove any empty ReadingOrder elements
    """
    ro = self.get_Page().get_ReadingOrder()
    if ro and not ro.get_OrderedGroup() and not ro.get_UnorderedGroup():
        self.get_Page().set_ReadingOrder(None)
