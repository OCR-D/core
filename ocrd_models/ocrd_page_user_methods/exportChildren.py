def exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"', name_='OrderedGroupType', fromsubclass_=False, pretty_print=True):
    eol_ = '\n' if pretty_print else ''
    namespaceprefix_ = 'pc:'
    if self.UserDefined is not None:
        self.UserDefined.export(outfile, level, namespaceprefix_, namespacedef_='', name_='UserDefined', pretty_print=pretty_print)
    for Labels_ in self.Labels:
        Labels_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='Labels', pretty_print=pretty_print)
    cleaned = []
    # remove emtpy groups and replace with RegionRefIndexedType
    for entry in self.get_AllIndexed():
        if isinstance(entry, (UnorderedGroupIndexedType, OrderedGroupIndexedType)) and not entry.get_AllIndexed():
            rri = RegionRefIndexedType.factory(parent_object_=self)
            rri.index = entry.index
            rri.regionRef = entry.regionRef
            cleaned.append(rri)
        else:
            cleaned.append(entry)
    for entry in cleaned:
        entry.export(outfile, level, namespaceprefix_, namespacedef_='', name_=entry.__class__.__name__[:-4], pretty_print=pretty_print)

