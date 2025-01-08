# pylint: disable=line-too-long,invalid-name,missing-module-docstring,missing-function-docstring
def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"', name_='OrderedGroupType', fromsubclass_=False, pretty_print=True): # pylint: disable=unused-argument,too-many-arguments
    if pretty_print:
        eol_ = '\n'
    else:
        eol_ = ''
    if self.UserDefined is not None:
        namespaceprefix_ = self.UserDefined_nsprefix_ + ':' if (UseCapturedNS_ and self.UserDefined_nsprefix_) else ''
        self.UserDefined.export(outfile, level, namespaceprefix_, namespacedef_='', name_='UserDefined', pretty_print=pretty_print)
    for Labels_ in self.Labels:
        namespaceprefix_ = self.Labels_nsprefix_ + ':' if (UseCapturedNS_ and self.Labels_nsprefix_) else ''
        Labels_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='Labels', pretty_print=pretty_print)
    cleaned = []
    def replaceWithRRI(group):
        rri = RegionRefIndexedType.factory(parent_object_=self) # pylint: disable=undefined-variable
        rri.index = group.index
        rri.regionRef = group.regionRef
        cleaned.append(rri)
    # remove empty groups and replace with RegionRefIndexedType
    for entry in self.get_AllIndexed():
        # pylint: disable=undefined-variable
        if isinstance(entry, (OrderedGroupIndexedType)) and not entry.get_AllIndexed():
            replaceWithRRI(entry)
        elif isinstance(entry, UnorderedGroupIndexedType) and not entry.get_UnorderedGroupChildren():
            replaceWithRRI(entry)
        else:
            cleaned.append(entry)
    for entry in cleaned:
        entry.export(outfile, level, entry.ns_prefix_, namespacedef_='', name_=entry.__class__.__name__[:-4], pretty_print=pretty_print)
