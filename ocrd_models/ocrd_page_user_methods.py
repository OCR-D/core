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
# export children sorted by index of the childelement
#
sort_children_by_index = MethodSpec(name='exportChildren',
    source=r'''
    def exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"', name_='OrderedGroupType', fromsubclass_=False, pretty_print=True):
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
        for RegionRefIndexed_ in sorted(self.RegionRefIndexed, key=lambda rri: rri.index):
            namespaceprefix_ = self.RegionRefIndexed_nsprefix_ + ':' if (UseCapturedNS_ and self.RegionRefIndexed_nsprefix_) else ''
            RegionRefIndexed_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='RegionRefIndexed', pretty_print=pretty_print)
        for OrderedGroupIndexed_ in sorted(self.OrderedGroupIndexed, key=lambda ogi: ogi.index):
            namespaceprefix_ = self.OrderedGroupIndexed_nsprefix_ + ':' if (UseCapturedNS_ and self.OrderedGroupIndexed_nsprefix_) else ''
            OrderedGroupIndexed_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='OrderedGroupIndexed', pretty_print=pretty_print)
        for UnorderedGroupIndexed_ in sorted(self.UnorderedGroupIndexed, key=lambda ugi: ugi.index):
            namespaceprefix_ = self.UnorderedGroupIndexed_nsprefix_ + ':' if (UseCapturedNS_ and self.UnorderedGroupIndexed_nsprefix_) else ''
            UnorderedGroupIndexed_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='UnorderedGroupIndexed', pretty_print=pretty_print)
''',
    class_names=r'OrderedGroupType$',
    )
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
    sort_children_by_index,
    )


def test():
    for spec in METHOD_SPECS:
        spec.show()

def main():
    test()


if __name__ == '__main__':
    main()
