# pylint: disable=invalid-name,missing-module-docstring,line-too-long
def get_AllIndexed(self, classes=None, index_sort=True):
    """
    Get all indexed children sorted by their ``@index``.

    Arguments:
        classes (list): Type of children to return. Default: ['RegionRef', 'OrderedGroup', 'UnorderedGroup']
        index_sort (boolean): Whether to sort by ``@index``
    """
    if not classes:
        classes = ['RegionRef', 'OrderedGroup', 'UnorderedGroup']
    ret = []
    for class_ in classes:
        ret += getattr(self, 'get_{}Indexed'.format(class_))()
    if index_sort:
        return sorted(ret, key=lambda x: x.index)
    return ret
