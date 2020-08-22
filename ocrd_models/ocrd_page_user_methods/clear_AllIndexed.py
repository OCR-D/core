def clear_AllIndexed(self):
    ret = self.get_AllIndexed()
    self.set_RegionRefIndexed([])
    self.set_OrderedGroupIndexed([])
    self.set_UnorderedGroupIndexed([])
    return ret

