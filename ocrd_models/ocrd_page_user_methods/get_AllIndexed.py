def get_AllIndexed(self):
    return sorted(self.get_RegionRefIndexed() + self.get_OrderedGroupIndexed() + self.get_UnorderedGroupIndexed(), key=lambda x: x.index)

