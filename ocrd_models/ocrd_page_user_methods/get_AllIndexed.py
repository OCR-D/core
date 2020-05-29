# pylint: disable=invalid-name,missing-module-docstring,line-too-long
def get_AllIndexed(self, classes=None):
    """
    Get all indexed children sorted by their ``@index``.

    Arguments:
        classes (list): Type of children to return. Default: ['RegionRef', 'OrderedGroup', 'UnorderedGroup']
    """
    if not classes:
        classes = ['RegionRef', 'OrderedGroup', 'UnorderedGroup']
    ret = []
    if 'RegionRef' in classes:
        ret += self.get_RegionRefIndexed()
    if 'OrderedGroup' in classes:
        ret += self.get_OrderedGroupIndexed()
    if 'UnorderedGroup' in classes:
        ret += self.get_UnorderedGroupIndexed()
    return sorted(ret, key=lambda x: x.index)
