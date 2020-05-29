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
    for class_ in classes:
        ret += getattr(self, 'get_{}Indexed'.format(class_))()
    return sorted(ret, key=lambda x: x.index)
