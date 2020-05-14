#!/usr/bin/env python

# source: https://bitbucket.org/dkuhlman/generateds/src/default/gends_user_methods.py

import re

#
# You must include the following class definition at the top of
#   your method specification file.
#
class MethodSpec():
    def __init__(self, name='', source='', class_names='',
            class_names_compiled=None):
        """MethodSpec -- A specification of a method.
        Member variables:
            name -- The method name
            source -- The source code for the method.  Must be
                indented to fit in a class definition.
            class_names -- A regular expression that must match the
                class names in which the method is to be inserted.
            class_names_compiled -- The compiled class names.
                generateDS.py will do this compile for you.
        """
        self.name = name
        self.source = source
        if class_names is None:
            self.class_names = ('.*', )
        else:
            self.class_names = class_names
        if class_names_compiled is None:
            self.class_names_compiled = re.compile(self.class_names)
        else:
            self.class_names_compiled = class_names_compiled
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_source(self):
        return self.source
    def set_source(self, source):
        self.source = source
    def get_class_names(self):
        return self.class_names
    def set_class_names(self, class_names):
        self.class_names = class_names
        self.class_names_compiled = re.compile(class_names)
    def get_class_names_compiled(self):
        return self.class_names_compiled
    def set_class_names_compiled(self, class_names_compiled):
        self.class_names_compiled = class_names_compiled
    def match_name(self, class_name):
        """Match against the name of the class currently being generated.
        If this method returns True, the method will be inserted in
          the generated class.
        """
        if self.class_names_compiled.search(class_name):
            return True
        return False
    def get_interpolated_source(self, values_dict):
        """Get the method source code, interpolating values from values_dict
        into it.  The source returned by this method is inserted into
        the generated class.
        """
        source = self.source % values_dict
        return source
    def show(self):
        print('specification:')
        print('    name: %s' % (self.name, ))
        print(self.source)
        print('    class_names: %s' % (self.class_names, ))
        print('    names pat  : %s' % (self.class_names_compiled.pattern, ))


#
# Provide one or more method specification such as the following.
# Notes:
# - Each generated class contains a class variable _member_data_items.
#   This variable contains a list of instances of class _MemberSpec.
#   See the definition of class _MemberSpec near the top of the
#   generated superclass file and also section "User Methods" in
#   the documentation, as well as the examples below.

#
# Replace the following method specifications with your own.

#
# List all *Regions on the PAGE
#
get_AllRegions = MethodSpec(name='get_AllRegions',
    source=r'''
    def get_AllRegions(self, regions=None, reading_order=False):
        """"
        Get all the *Region element or only those provided by ``regions``.
        Returned in random order unless ``reading_order`` is set (NOT CURRENTLY IMPLEMENTED)
        """
        if reading_order:
            reading_order = self.get_ReadingOrder()
        if not regions:
            regions = ['Advert', 'Chart', 'Chem', 'Custom', 'Graphic', 'Image', 'LineDrawing', 'Map', 'Maths', 'Music', 'Noise', 'Separator', 'Table', 'Text', 'Unknown']
        ret = []
        for region in regions:
            ret += getattr(self, 'get_{}Region'.format(region))()
        if reading_order:
            reading_order = reading_order.get_OrderedGroup() or reading_order.get_UnorderedGroup()
        if reading_order:
            def get_recursive_reading_order(rogroup):
                if isinstance(rogroup, (OrderedGroupType, OrderedGroupIndexedType)):
                    elements = rogroup.get_AllIndexed()
                if isinstance(rogroup, (UnorderedGroupType, UnorderedGroupIndexedType)):
                    elements = (rogroup.get_RegionRef() + rogroup.get_OrderedGroup() + rogroup.get_UnorderedGroup())
                regionrefs = list()
                for elem in elements:
                    regionrefs.append(elem.get_regionRef())
                    if not isinstance(elem, (RegionRefType, RegionRefIndexedType)):
                        regionrefs.extend(get_recursive_reading_order(elem))
                return regionrefs
            reading_order = get_recursive_reading_order(reading_order)
        if reading_order:
            ret = dict([(region.id, region) for region in ret])
            return [ret[region_id] for region_id in reading_order if region_id in ret]
        else:
            return ret
    ''', class_names=r'^(PageType)$')

#
# List all *Indexed children sorted by @index
#
get_AllIndexed = MethodSpec(name='get_AllIndexed',
    source=r'''
    def get_AllIndexed(self):
        return sorted(self.get_RegionRefIndexed() + self.get_OrderedGroupIndexed() + self.get_UnorderedGroupIndexed(), key=lambda x : x.index) ''', class_names=r'^(OrderedGroupType|OrderedGroupIndexedType)$')

#
# Clear all *Indexed children sorted by @index
#
clear_AllIndexed = MethodSpec(name='clear_AllIndexed',
    source=r'''
    def clear_AllIndexed(self):
        ret = self.get_AllIndexed()
        self.set_RegionRefIndexed([])
        self.set_OrderedGroupIndexed([])
        self.set_UnorderedGroupIndexed([])
        return ret
''', class_names=r'^(OrderedGroupType|OrderedGroupIndexedType)$')

#
# Add all *Indexed children sorted by @index
#
add_AllIndexed = MethodSpec(name='add_AllIndexed',
    source=r'''
    def add_AllIndexed(self, elements):
        if not isinstance(elements, list):
            elements = [elements]
        for element in sorted(elements, key=lambda x : x.index):
            if isinstance(element, RegionRefIndexedType):
                self.add_RegionRefIndexed(element)
            elif isinstance(element, OrderedGroupIndexedType):
                self.add_OrderedGroupIndexed(element)
            elif isinstance(element, UnorderedGroupIndexedType):
                self.add_UnorderedGroupIndexed(element)
        return self.get_AllIndexed()
''', class_names=r'^(OrderedGroupType|OrderedGroupIndexedType)$')


#
# export children sorted by index of the childelement
#
exportChildren = MethodSpec(name='exportChildren',
    source=r'''
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
''', class_names=r'^(OrderedGroupType|OrderedGroupIndexedType)$')
#
# Hash by memory adress/id()
#
hash_by_id = MethodSpec(name='hash',
    source='''\
    def __hash__(self):
        return hash(self.id)
''',
    class_names=r'^.*$',
    )
#
# Provide a list of your method specifications.
#   This list of specifications must be named METHOD_SPECS.
#
METHOD_SPECS = (
    hash_by_id,
    exportChildren,
    get_AllIndexed,
    add_AllIndexed,
    get_AllRegions,
    clear_AllIndexed,
    )


def test():
    for spec in METHOD_SPECS:
        spec.show()

def main():
    test()


if __name__ == '__main__':
    main()
