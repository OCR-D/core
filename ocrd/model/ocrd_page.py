# ./ocrd_page.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:8f42b6e01cd3938f035d6626191915c514c281ab
# Generated 2018-04-23 23:12:15.264378 by PyXB version 1.2.6 using Python 3.6.3.final.0
# Namespace http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:ff106b96-473a-11e8-b231-00155d15430e')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.6'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 506, 3)
    _Documentation = None
STD_ANON._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=STD_ANON, value=pyxb.binding.datatypes.integer(0))
STD_ANON._InitializeFacetMap(STD_ANON._CF_minInclusive)
_module_typeBindings.STD_ANON = STD_ANON

# Atomic simple type: [anonymous]
class STD_ANON_ (pyxb.binding.datatypes.float):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 516, 12)
    _Documentation = None
STD_ANON_._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=STD_ANON_, value=pyxb.binding.datatypes.float(0.0))
STD_ANON_._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=STD_ANON_, value=pyxb.binding.datatypes.float(1.0))
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_minInclusive,
   STD_ANON_._CF_maxInclusive)
_module_typeBindings.STD_ANON_ = STD_ANON_

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ColourSimpleType
class ColourSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ColourSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1169, 4)
    _Documentation = None
ColourSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ColourSimpleType, enum_prefix=None)
ColourSimpleType.black = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='black', tag='black')
ColourSimpleType.blue = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='blue', tag='blue')
ColourSimpleType.brown = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='brown', tag='brown')
ColourSimpleType.cyan = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='cyan', tag='cyan')
ColourSimpleType.green = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='green', tag='green')
ColourSimpleType.grey = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='grey', tag='grey')
ColourSimpleType.indigo = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='indigo', tag='indigo')
ColourSimpleType.magenta = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='magenta', tag='magenta')
ColourSimpleType.orange = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='orange', tag='orange')
ColourSimpleType.pink = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='pink', tag='pink')
ColourSimpleType.red = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='red', tag='red')
ColourSimpleType.turquoise = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='turquoise', tag='turquoise')
ColourSimpleType.violet = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='violet', tag='violet')
ColourSimpleType.white = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='white', tag='white')
ColourSimpleType.yellow = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='yellow', tag='yellow')
ColourSimpleType.other = ColourSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
ColourSimpleType._InitializeFacetMap(ColourSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ColourSimpleType', ColourSimpleType)
_module_typeBindings.ColourSimpleType = ColourSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ReadingDirectionSimpleType
class ReadingDirectionSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ReadingDirectionSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1189, 4)
    _Documentation = None
ReadingDirectionSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ReadingDirectionSimpleType, enum_prefix=None)
ReadingDirectionSimpleType.left_to_right = ReadingDirectionSimpleType._CF_enumeration.addEnumeration(unicode_value='left-to-right', tag='left_to_right')
ReadingDirectionSimpleType.right_to_left = ReadingDirectionSimpleType._CF_enumeration.addEnumeration(unicode_value='right-to-left', tag='right_to_left')
ReadingDirectionSimpleType.top_to_bottom = ReadingDirectionSimpleType._CF_enumeration.addEnumeration(unicode_value='top-to-bottom', tag='top_to_bottom')
ReadingDirectionSimpleType.bottom_to_top = ReadingDirectionSimpleType._CF_enumeration.addEnumeration(unicode_value='bottom-to-top', tag='bottom_to_top')
ReadingDirectionSimpleType._InitializeFacetMap(ReadingDirectionSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ReadingDirectionSimpleType', ReadingDirectionSimpleType)
_module_typeBindings.ReadingDirectionSimpleType = ReadingDirectionSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextLineOrderSimpleType
class TextLineOrderSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextLineOrderSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1197, 4)
    _Documentation = None
TextLineOrderSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TextLineOrderSimpleType, enum_prefix=None)
TextLineOrderSimpleType.top_to_bottom = TextLineOrderSimpleType._CF_enumeration.addEnumeration(unicode_value='top-to-bottom', tag='top_to_bottom')
TextLineOrderSimpleType.bottom_to_top = TextLineOrderSimpleType._CF_enumeration.addEnumeration(unicode_value='bottom-to-top', tag='bottom_to_top')
TextLineOrderSimpleType.left_to_right = TextLineOrderSimpleType._CF_enumeration.addEnumeration(unicode_value='left-to-right', tag='left_to_right')
TextLineOrderSimpleType.right_to_left = TextLineOrderSimpleType._CF_enumeration.addEnumeration(unicode_value='right-to-left', tag='right_to_left')
TextLineOrderSimpleType._InitializeFacetMap(TextLineOrderSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'TextLineOrderSimpleType', TextLineOrderSimpleType)
_module_typeBindings.TextLineOrderSimpleType = TextLineOrderSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextTypeSimpleType
class TextTypeSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextTypeSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1205, 4)
    _Documentation = None
TextTypeSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TextTypeSimpleType, enum_prefix=None)
TextTypeSimpleType.paragraph = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='paragraph', tag='paragraph')
TextTypeSimpleType.heading = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='heading', tag='heading')
TextTypeSimpleType.caption = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='caption', tag='caption')
TextTypeSimpleType.header = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='header', tag='header')
TextTypeSimpleType.footer = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='footer', tag='footer')
TextTypeSimpleType.page_number = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='page-number', tag='page_number')
TextTypeSimpleType.drop_capital = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='drop-capital', tag='drop_capital')
TextTypeSimpleType.credit = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='credit', tag='credit')
TextTypeSimpleType.floating = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='floating', tag='floating')
TextTypeSimpleType.signature_mark = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='signature-mark', tag='signature_mark')
TextTypeSimpleType.catch_word = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='catch-word', tag='catch_word')
TextTypeSimpleType.marginalia = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='marginalia', tag='marginalia')
TextTypeSimpleType.footnote = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='footnote', tag='footnote')
TextTypeSimpleType.footnote_continued = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='footnote-continued', tag='footnote_continued')
TextTypeSimpleType.endnote = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='endnote', tag='endnote')
TextTypeSimpleType.TOC_entry = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='TOC-entry', tag='TOC_entry')
TextTypeSimpleType.list_label = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='list-label', tag='list_label')
TextTypeSimpleType.other = TextTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
TextTypeSimpleType._InitializeFacetMap(TextTypeSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'TextTypeSimpleType', TextTypeSimpleType)
_module_typeBindings.TextTypeSimpleType = TextTypeSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PageTypeSimpleType
class PageTypeSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PageTypeSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1227, 4)
    _Documentation = None
PageTypeSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=PageTypeSimpleType, enum_prefix=None)
PageTypeSimpleType.front_cover = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='front-cover', tag='front_cover')
PageTypeSimpleType.back_cover = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='back-cover', tag='back_cover')
PageTypeSimpleType.title = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='title', tag='title')
PageTypeSimpleType.table_of_contents = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='table-of-contents', tag='table_of_contents')
PageTypeSimpleType.index = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='index', tag='index')
PageTypeSimpleType.content = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='content', tag='content')
PageTypeSimpleType.blank = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='blank', tag='blank')
PageTypeSimpleType.other = PageTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
PageTypeSimpleType._InitializeFacetMap(PageTypeSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'PageTypeSimpleType', PageTypeSimpleType)
_module_typeBindings.PageTypeSimpleType = PageTypeSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LanguageSimpleType
class LanguageSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """iso15924 2016-07-14"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LanguageSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1240, 4)
    _Documentation = 'iso15924 2016-07-14'
LanguageSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=LanguageSimpleType, enum_prefix=None)
LanguageSimpleType.Abkhaz = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Abkhaz', tag='Abkhaz')
LanguageSimpleType.Afar = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Afar', tag='Afar')
LanguageSimpleType.Afrikaans = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Afrikaans', tag='Afrikaans')
LanguageSimpleType.Akan = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Akan', tag='Akan')
LanguageSimpleType.Albanian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Albanian', tag='Albanian')
LanguageSimpleType.Amharic = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Amharic', tag='Amharic')
LanguageSimpleType.Arabic = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Arabic', tag='Arabic')
LanguageSimpleType.Aragonese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Aragonese', tag='Aragonese')
LanguageSimpleType.Armenian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Armenian', tag='Armenian')
LanguageSimpleType.Assamese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Assamese', tag='Assamese')
LanguageSimpleType.Avaric = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Avaric', tag='Avaric')
LanguageSimpleType.Avestan = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Avestan', tag='Avestan')
LanguageSimpleType.Aymara = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Aymara', tag='Aymara')
LanguageSimpleType.Azerbaijani = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Azerbaijani', tag='Azerbaijani')
LanguageSimpleType.Bambara = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bambara', tag='Bambara')
LanguageSimpleType.Bashkir = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bashkir', tag='Bashkir')
LanguageSimpleType.Basque = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Basque', tag='Basque')
LanguageSimpleType.Belarusian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Belarusian', tag='Belarusian')
LanguageSimpleType.Bengali = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bengali', tag='Bengali')
LanguageSimpleType.Bihari = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bihari', tag='Bihari')
LanguageSimpleType.Bislama = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bislama', tag='Bislama')
LanguageSimpleType.Bosnian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bosnian', tag='Bosnian')
LanguageSimpleType.Breton = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Breton', tag='Breton')
LanguageSimpleType.Bulgarian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Bulgarian', tag='Bulgarian')
LanguageSimpleType.Burmese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Burmese', tag='Burmese')
LanguageSimpleType.Cambodian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Cambodian', tag='Cambodian')
LanguageSimpleType.Cantonese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Cantonese', tag='Cantonese')
LanguageSimpleType.Catalan = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Catalan', tag='Catalan')
LanguageSimpleType.Chamorro = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Chamorro', tag='Chamorro')
LanguageSimpleType.Chechen = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Chechen', tag='Chechen')
LanguageSimpleType.Chichewa = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Chichewa', tag='Chichewa')
LanguageSimpleType.Chinese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Chinese', tag='Chinese')
LanguageSimpleType.Chuvash = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Chuvash', tag='Chuvash')
LanguageSimpleType.Cornish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Cornish', tag='Cornish')
LanguageSimpleType.Corsican = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Corsican', tag='Corsican')
LanguageSimpleType.Cree = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Cree', tag='Cree')
LanguageSimpleType.Croatian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Croatian', tag='Croatian')
LanguageSimpleType.Czech = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Czech', tag='Czech')
LanguageSimpleType.Danish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Danish', tag='Danish')
LanguageSimpleType.Divehi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Divehi', tag='Divehi')
LanguageSimpleType.Dutch = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Dutch', tag='Dutch')
LanguageSimpleType.Dzongkha = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Dzongkha', tag='Dzongkha')
LanguageSimpleType.English = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='English', tag='English')
LanguageSimpleType.Esperanto = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Esperanto', tag='Esperanto')
LanguageSimpleType.Estonian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Estonian', tag='Estonian')
LanguageSimpleType.Ewe = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ewe', tag='Ewe')
LanguageSimpleType.Faroese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Faroese', tag='Faroese')
LanguageSimpleType.Fijian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Fijian', tag='Fijian')
LanguageSimpleType.Finnish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Finnish', tag='Finnish')
LanguageSimpleType.French = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='French', tag='French')
LanguageSimpleType.Fula = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Fula', tag='Fula')
LanguageSimpleType.Gaelic = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Gaelic', tag='Gaelic')
LanguageSimpleType.Galician = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Galician', tag='Galician')
LanguageSimpleType.Ganda = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ganda', tag='Ganda')
LanguageSimpleType.Georgian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Georgian', tag='Georgian')
LanguageSimpleType.German = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='German', tag='German')
LanguageSimpleType.Greek = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Greek', tag='Greek')
LanguageSimpleType.Guaran = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Guaraní', tag='Guaran')
LanguageSimpleType.Gujarati = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Gujarati', tag='Gujarati')
LanguageSimpleType.Haitian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Haitian', tag='Haitian')
LanguageSimpleType.Hausa = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Hausa', tag='Hausa')
LanguageSimpleType.Hebrew = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Hebrew', tag='Hebrew')
LanguageSimpleType.Herero = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Herero', tag='Herero')
LanguageSimpleType.Hindi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Hindi', tag='Hindi')
LanguageSimpleType.Hiri_Motu = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Hiri Motu', tag='Hiri_Motu')
LanguageSimpleType.Hungarian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Hungarian', tag='Hungarian')
LanguageSimpleType.Icelandic = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Icelandic', tag='Icelandic')
LanguageSimpleType.Ido = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ido', tag='Ido')
LanguageSimpleType.Igbo = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Igbo', tag='Igbo')
LanguageSimpleType.Indonesian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Indonesian', tag='Indonesian')
LanguageSimpleType.Interlingua = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Interlingua', tag='Interlingua')
LanguageSimpleType.Interlingue = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Interlingue', tag='Interlingue')
LanguageSimpleType.Inuktitut = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Inuktitut', tag='Inuktitut')
LanguageSimpleType.Inupiaq = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Inupiaq', tag='Inupiaq')
LanguageSimpleType.Irish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Irish', tag='Irish')
LanguageSimpleType.Italian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Italian', tag='Italian')
LanguageSimpleType.Japanese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Japanese', tag='Japanese')
LanguageSimpleType.Javanese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Javanese', tag='Javanese')
LanguageSimpleType.Kalaallisut = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kalaallisut', tag='Kalaallisut')
LanguageSimpleType.Kannada = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kannada', tag='Kannada')
LanguageSimpleType.Kanuri = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kanuri', tag='Kanuri')
LanguageSimpleType.Kashmiri = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kashmiri', tag='Kashmiri')
LanguageSimpleType.Kazakh = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kazakh', tag='Kazakh')
LanguageSimpleType.Khmer = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Khmer', tag='Khmer')
LanguageSimpleType.Kikuyu = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kikuyu', tag='Kikuyu')
LanguageSimpleType.Kinyarwanda = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kinyarwanda', tag='Kinyarwanda')
LanguageSimpleType.Kirundi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kirundi', tag='Kirundi')
LanguageSimpleType.Komi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Komi', tag='Komi')
LanguageSimpleType.Kongo = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kongo', tag='Kongo')
LanguageSimpleType.Korean = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Korean', tag='Korean')
LanguageSimpleType.Kurdish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kurdish', tag='Kurdish')
LanguageSimpleType.Kwanyama = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kwanyama', tag='Kwanyama')
LanguageSimpleType.Kyrgyz = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Kyrgyz', tag='Kyrgyz')
LanguageSimpleType.Lao = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Lao', tag='Lao')
LanguageSimpleType.Latin = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Latin', tag='Latin')
LanguageSimpleType.Latvian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Latvian', tag='Latvian')
LanguageSimpleType.Limburgish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Limburgish', tag='Limburgish')
LanguageSimpleType.Lingala = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Lingala', tag='Lingala')
LanguageSimpleType.Lithuanian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Lithuanian', tag='Lithuanian')
LanguageSimpleType.Luba_Katanga = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Luba-Katanga', tag='Luba_Katanga')
LanguageSimpleType.Luxembourgish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Luxembourgish', tag='Luxembourgish')
LanguageSimpleType.Macedonian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Macedonian', tag='Macedonian')
LanguageSimpleType.Malagasy = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Malagasy', tag='Malagasy')
LanguageSimpleType.Malay = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Malay', tag='Malay')
LanguageSimpleType.Malayalam = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Malayalam', tag='Malayalam')
LanguageSimpleType.Maltese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Maltese', tag='Maltese')
LanguageSimpleType.Manx = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Manx', tag='Manx')
LanguageSimpleType.Mori = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Māori', tag='Mori')
LanguageSimpleType.Marathi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Marathi', tag='Marathi')
LanguageSimpleType.Marshallese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Marshallese', tag='Marshallese')
LanguageSimpleType.Mongolian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Mongolian', tag='Mongolian')
LanguageSimpleType.Nauru = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Nauru', tag='Nauru')
LanguageSimpleType.Navajo = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Navajo', tag='Navajo')
LanguageSimpleType.Ndonga = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ndonga', tag='Ndonga')
LanguageSimpleType.Nepali = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Nepali', tag='Nepali')
LanguageSimpleType.North_Ndebele = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='North Ndebele', tag='North_Ndebele')
LanguageSimpleType.Northern_Sami = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Northern Sami', tag='Northern_Sami')
LanguageSimpleType.Norwegian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Norwegian', tag='Norwegian')
LanguageSimpleType.Norwegian_Bokml = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Norwegian Bokmål', tag='Norwegian_Bokml')
LanguageSimpleType.Norwegian_Nynorsk = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Norwegian Nynorsk', tag='Norwegian_Nynorsk')
LanguageSimpleType.Nuosu = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Nuosu', tag='Nuosu')
LanguageSimpleType.Occitan = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Occitan', tag='Occitan')
LanguageSimpleType.Ojibwe = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ojibwe', tag='Ojibwe')
LanguageSimpleType.Old_Church_Slavonic = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Old Church Slavonic', tag='Old_Church_Slavonic')
LanguageSimpleType.Oriya = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Oriya', tag='Oriya')
LanguageSimpleType.Oromo = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Oromo', tag='Oromo')
LanguageSimpleType.Ossetian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ossetian', tag='Ossetian')
LanguageSimpleType.Pli = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Pāli', tag='Pli')
LanguageSimpleType.Panjabi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Panjabi', tag='Panjabi')
LanguageSimpleType.Pashto = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Pashto', tag='Pashto')
LanguageSimpleType.Persian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Persian', tag='Persian')
LanguageSimpleType.Polish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Polish', tag='Polish')
LanguageSimpleType.Portuguese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Portuguese', tag='Portuguese')
LanguageSimpleType.Punjabi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Punjabi', tag='Punjabi')
LanguageSimpleType.Quechua = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Quechua', tag='Quechua')
LanguageSimpleType.Romanian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Romanian', tag='Romanian')
LanguageSimpleType.Romansh = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Romansh', tag='Romansh')
LanguageSimpleType.Russian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Russian', tag='Russian')
LanguageSimpleType.Samoan = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Samoan', tag='Samoan')
LanguageSimpleType.Sango = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Sango', tag='Sango')
LanguageSimpleType.Sanskrit = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Sanskrit', tag='Sanskrit')
LanguageSimpleType.Sardinian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Sardinian', tag='Sardinian')
LanguageSimpleType.Serbian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Serbian', tag='Serbian')
LanguageSimpleType.Shona = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Shona', tag='Shona')
LanguageSimpleType.Sindhi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Sindhi', tag='Sindhi')
LanguageSimpleType.Sinhala = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Sinhala', tag='Sinhala')
LanguageSimpleType.Slovak = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Slovak', tag='Slovak')
LanguageSimpleType.Slovene = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Slovene', tag='Slovene')
LanguageSimpleType.Somali = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Somali', tag='Somali')
LanguageSimpleType.South_Ndebele = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='South Ndebele', tag='South_Ndebele')
LanguageSimpleType.Southern_Sotho = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Southern Sotho', tag='Southern_Sotho')
LanguageSimpleType.Spanish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Spanish', tag='Spanish')
LanguageSimpleType.Sundanese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Sundanese', tag='Sundanese')
LanguageSimpleType.Swahili = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Swahili', tag='Swahili')
LanguageSimpleType.Swati = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Swati', tag='Swati')
LanguageSimpleType.Swedish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Swedish', tag='Swedish')
LanguageSimpleType.Tagalog = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tagalog', tag='Tagalog')
LanguageSimpleType.Tahitian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tahitian', tag='Tahitian')
LanguageSimpleType.Tajik = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tajik', tag='Tajik')
LanguageSimpleType.Tamil = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tamil', tag='Tamil')
LanguageSimpleType.Tatar = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tatar', tag='Tatar')
LanguageSimpleType.Telugu = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Telugu', tag='Telugu')
LanguageSimpleType.Thai = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Thai', tag='Thai')
LanguageSimpleType.Tibetan = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tibetan', tag='Tibetan')
LanguageSimpleType.Tigrinya = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tigrinya', tag='Tigrinya')
LanguageSimpleType.Tonga = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tonga', tag='Tonga')
LanguageSimpleType.Tsonga = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tsonga', tag='Tsonga')
LanguageSimpleType.Tswana = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Tswana', tag='Tswana')
LanguageSimpleType.Turkish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Turkish', tag='Turkish')
LanguageSimpleType.Turkmen = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Turkmen', tag='Turkmen')
LanguageSimpleType.Twi = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Twi', tag='Twi')
LanguageSimpleType.Uighur = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Uighur', tag='Uighur')
LanguageSimpleType.Ukrainian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Ukrainian', tag='Ukrainian')
LanguageSimpleType.Urdu = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Urdu', tag='Urdu')
LanguageSimpleType.Uzbek = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Uzbek', tag='Uzbek')
LanguageSimpleType.Venda = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Venda', tag='Venda')
LanguageSimpleType.Vietnamese = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Vietnamese', tag='Vietnamese')
LanguageSimpleType.Volapk = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Volapük', tag='Volapk')
LanguageSimpleType.Walloon = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Walloon', tag='Walloon')
LanguageSimpleType.Welsh = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Welsh', tag='Welsh')
LanguageSimpleType.Western_Frisian = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Western Frisian', tag='Western_Frisian')
LanguageSimpleType.Wolof = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Wolof', tag='Wolof')
LanguageSimpleType.Xhosa = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Xhosa', tag='Xhosa')
LanguageSimpleType.Yiddish = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Yiddish', tag='Yiddish')
LanguageSimpleType.Yoruba = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Yoruba', tag='Yoruba')
LanguageSimpleType.Zhuang = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Zhuang', tag='Zhuang')
LanguageSimpleType.Zulu = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='Zulu', tag='Zulu')
LanguageSimpleType.other = LanguageSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
LanguageSimpleType._InitializeFacetMap(LanguageSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'LanguageSimpleType', LanguageSimpleType)
_module_typeBindings.LanguageSimpleType = LanguageSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ScriptSimpleType
class ScriptSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ScriptSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1436, 4)
    _Documentation = None
ScriptSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ScriptSimpleType, enum_prefix=None)
ScriptSimpleType.Adlm___Adlam = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Adlm - Adlam', tag='Adlm___Adlam')
ScriptSimpleType.Afak___Afaka = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Afak - Afaka', tag='Afak___Afaka')
ScriptSimpleType.Aghb___Caucasian_Albanian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Aghb - Caucasian Albanian', tag='Aghb___Caucasian_Albanian')
ScriptSimpleType.Ahom___Ahom_Tai_Ahom = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Ahom - Ahom, Tai Ahom', tag='Ahom___Ahom_Tai_Ahom')
ScriptSimpleType.Arab___Arabic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Arab - Arabic', tag='Arab___Arabic')
ScriptSimpleType.Aran___Arabic_Nastaliq_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Aran - Arabic (Nastaliq variant)', tag='Aran___Arabic_Nastaliq_variant')
ScriptSimpleType.Armi___Imperial_Aramaic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Armi - Imperial Aramaic', tag='Armi___Imperial_Aramaic')
ScriptSimpleType.Armn___Armenian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Armn - Armenian', tag='Armn___Armenian')
ScriptSimpleType.Avst___Avestan = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Avst - Avestan', tag='Avst___Avestan')
ScriptSimpleType.Bali___Balinese = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Bali - Balinese', tag='Bali___Balinese')
ScriptSimpleType.Bamu___Bamum = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Bamu - Bamum', tag='Bamu___Bamum')
ScriptSimpleType.Bass___Bassa_Vah = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Bass - Bassa Vah', tag='Bass___Bassa_Vah')
ScriptSimpleType.Batk___Batak = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Batk - Batak', tag='Batk___Batak')
ScriptSimpleType.Beng___Bengali = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Beng - Bengali', tag='Beng___Bengali')
ScriptSimpleType.Bhks___Bhaiksuki = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Bhks - Bhaiksuki', tag='Bhks___Bhaiksuki')
ScriptSimpleType.Blis___Blissymbols = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Blis - Blissymbols', tag='Blis___Blissymbols')
ScriptSimpleType.Bopo___Bopomofo = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Bopo - Bopomofo', tag='Bopo___Bopomofo')
ScriptSimpleType.Brah___Brahmi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Brah - Brahmi', tag='Brah___Brahmi')
ScriptSimpleType.Brai___Braille = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Brai - Braille', tag='Brai___Braille')
ScriptSimpleType.Bugi___Buginese = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Bugi - Buginese', tag='Bugi___Buginese')
ScriptSimpleType.Buhd___Buhid = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Buhd - Buhid', tag='Buhd___Buhid')
ScriptSimpleType.Cakm___Chakma = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cakm - Chakma', tag='Cakm___Chakma')
ScriptSimpleType.Cans___Unified_Canadian_Aboriginal_Syllabics = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cans - Unified Canadian Aboriginal Syllabics', tag='Cans___Unified_Canadian_Aboriginal_Syllabics')
ScriptSimpleType.Cari___Carian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cari - Carian', tag='Cari___Carian')
ScriptSimpleType.Cham___Cham = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cham - Cham', tag='Cham___Cham')
ScriptSimpleType.Cher___Cherokee = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cher - Cherokee', tag='Cher___Cherokee')
ScriptSimpleType.Cirt___Cirth = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cirt - Cirth', tag='Cirt___Cirth')
ScriptSimpleType.Copt___Coptic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Copt - Coptic', tag='Copt___Coptic')
ScriptSimpleType.Cprt___Cypriot = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cprt - Cypriot', tag='Cprt___Cypriot')
ScriptSimpleType.Cyrl___Cyrillic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cyrl - Cyrillic', tag='Cyrl___Cyrillic')
ScriptSimpleType.Cyrs___Cyrillic_Old_Church_Slavonic_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Cyrs - Cyrillic (Old Church Slavonic variant)', tag='Cyrs___Cyrillic_Old_Church_Slavonic_variant')
ScriptSimpleType.Deva___Devanagari_Nagari = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Deva - Devanagari (Nagari)', tag='Deva___Devanagari_Nagari')
ScriptSimpleType.Dsrt___Deseret_Mormon = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Dsrt - Deseret (Mormon)', tag='Dsrt___Deseret_Mormon')
ScriptSimpleType.Dupl___Duployan_shorthand_Duployan_stenography = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Dupl - Duployan shorthand, Duployan stenography', tag='Dupl___Duployan_shorthand_Duployan_stenography')
ScriptSimpleType.Egyd___Egyptian_demotic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Egyd - Egyptian demotic', tag='Egyd___Egyptian_demotic')
ScriptSimpleType.Egyh___Egyptian_hieratic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Egyh - Egyptian hieratic', tag='Egyh___Egyptian_hieratic')
ScriptSimpleType.Egyp___Egyptian_hieroglyphs = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Egyp - Egyptian hieroglyphs', tag='Egyp___Egyptian_hieroglyphs')
ScriptSimpleType.Elba___Elbasan = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Elba - Elbasan', tag='Elba___Elbasan')
ScriptSimpleType.Ethi___Ethiopic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Ethi - Ethiopic', tag='Ethi___Ethiopic')
ScriptSimpleType.Geok___Khutsuri_Asomtavruli_and_Nuskhuri = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Geok - Khutsuri (Asomtavruli and Nuskhuri)', tag='Geok___Khutsuri_Asomtavruli_and_Nuskhuri')
ScriptSimpleType.Geor___Georgian_Mkhedruli = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Geor - Georgian (Mkhedruli)', tag='Geor___Georgian_Mkhedruli')
ScriptSimpleType.Glag___Glagolitic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Glag - Glagolitic', tag='Glag___Glagolitic')
ScriptSimpleType.Goth___Gothic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Goth - Gothic', tag='Goth___Gothic')
ScriptSimpleType.Gran___Grantha = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Gran - Grantha', tag='Gran___Grantha')
ScriptSimpleType.Grek___Greek = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Grek - Greek', tag='Grek___Greek')
ScriptSimpleType.Gujr___Gujarati = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Gujr - Gujarati', tag='Gujr___Gujarati')
ScriptSimpleType.Guru___Gurmukhi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Guru - Gurmukhi', tag='Guru___Gurmukhi')
ScriptSimpleType.Hanb___Han_with_Bopomofo = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hanb - Han with Bopomofo', tag='Hanb___Han_with_Bopomofo')
ScriptSimpleType.Hang___Hangul = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hang - Hangul', tag='Hang___Hangul')
ScriptSimpleType.Hani___Han_Hanzi_Kanji_Hanja = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hani - Han (Hanzi, Kanji, Hanja)', tag='Hani___Han_Hanzi_Kanji_Hanja')
ScriptSimpleType.Hano___Hanunoo_Hanuno = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hano - Hanunoo (Hanunóo)', tag='Hano___Hanunoo_Hanuno')
ScriptSimpleType.Hans___Han_Simplified_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hans - Han (Simplified variant)', tag='Hans___Han_Simplified_variant')
ScriptSimpleType.Hant___Han_Traditional_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hant - Han (Traditional variant)', tag='Hant___Han_Traditional_variant')
ScriptSimpleType.Hatr___Hatran = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hatr - Hatran', tag='Hatr___Hatran')
ScriptSimpleType.Hebr___Hebrew = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hebr - Hebrew', tag='Hebr___Hebrew')
ScriptSimpleType.Hira___Hiragana = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hira - Hiragana', tag='Hira___Hiragana')
ScriptSimpleType.Hluw___Anatolian_Hieroglyphs = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hluw - Anatolian Hieroglyphs', tag='Hluw___Anatolian_Hieroglyphs')
ScriptSimpleType.Hmng___Pahawh_Hmong = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hmng - Pahawh Hmong', tag='Hmng___Pahawh_Hmong')
ScriptSimpleType.Hrkt___Japanese_syllabaries = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hrkt - Japanese syllabaries', tag='Hrkt___Japanese_syllabaries')
ScriptSimpleType.Hung___Old_Hungarian_Hungarian_Runic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Hung - Old Hungarian (Hungarian Runic)', tag='Hung___Old_Hungarian_Hungarian_Runic')
ScriptSimpleType.Inds___Indus_Harappan = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Inds - Indus (Harappan)', tag='Inds___Indus_Harappan')
ScriptSimpleType.Ital___Old_Italic_Etruscan_Oscan_etc = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Ital - Old Italic (Etruscan, Oscan etc.)', tag='Ital___Old_Italic_Etruscan_Oscan_etc')
ScriptSimpleType.Jamo___Jamo = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Jamo - Jamo', tag='Jamo___Jamo')
ScriptSimpleType.Java___Javanese = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Java - Javanese', tag='Java___Javanese')
ScriptSimpleType.Jpan___Japanese = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Jpan - Japanese', tag='Jpan___Japanese')
ScriptSimpleType.Jurc___Jurchen = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Jurc - Jurchen', tag='Jurc___Jurchen')
ScriptSimpleType.Kali___Kayah_Li = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kali - Kayah Li', tag='Kali___Kayah_Li')
ScriptSimpleType.Kana___Katakana = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kana - Katakana', tag='Kana___Katakana')
ScriptSimpleType.Khar___Kharoshthi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Khar - Kharoshthi', tag='Khar___Kharoshthi')
ScriptSimpleType.Khmr___Khmer = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Khmr - Khmer', tag='Khmr___Khmer')
ScriptSimpleType.Khoj___Khojki = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Khoj - Khojki', tag='Khoj___Khojki')
ScriptSimpleType.Kitl___Khitan_large_script = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kitl - Khitan large script', tag='Kitl___Khitan_large_script')
ScriptSimpleType.Kits___Khitan_small_script = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kits - Khitan small script', tag='Kits___Khitan_small_script')
ScriptSimpleType.Knda___Kannada = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Knda - Kannada', tag='Knda___Kannada')
ScriptSimpleType.Kore___Korean_alias_for_Hangul__Han = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kore - Korean (alias for Hangul + Han)', tag='Kore___Korean_alias_for_Hangul__Han')
ScriptSimpleType.Kpel___Kpelle = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kpel - Kpelle', tag='Kpel___Kpelle')
ScriptSimpleType.Kthi___Kaithi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Kthi - Kaithi', tag='Kthi___Kaithi')
ScriptSimpleType.Lana___Tai_Tham_Lanna = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Lana - Tai Tham (Lanna)', tag='Lana___Tai_Tham_Lanna')
ScriptSimpleType.Laoo___Lao = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Laoo - Lao', tag='Laoo___Lao')
ScriptSimpleType.Latf___Latin_Fraktur_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Latf - Latin (Fraktur variant)', tag='Latf___Latin_Fraktur_variant')
ScriptSimpleType.Latg___Latin_Gaelic_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Latg - Latin (Gaelic variant)', tag='Latg___Latin_Gaelic_variant')
ScriptSimpleType.Latn___Latin = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Latn - Latin', tag='Latn___Latin')
ScriptSimpleType.Leke___Leke = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Leke - Leke', tag='Leke___Leke')
ScriptSimpleType.Lepc___Lepcha_Rng = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Lepc - Lepcha (Róng)', tag='Lepc___Lepcha_Rng')
ScriptSimpleType.Limb___Limbu = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Limb - Limbu', tag='Limb___Limbu')
ScriptSimpleType.Lina___Linear_A = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Lina - Linear A', tag='Lina___Linear_A')
ScriptSimpleType.Linb___Linear_B = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Linb - Linear B', tag='Linb___Linear_B')
ScriptSimpleType.Lisu___Lisu_Fraser = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Lisu - Lisu (Fraser)', tag='Lisu___Lisu_Fraser')
ScriptSimpleType.Loma___Loma = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Loma - Loma', tag='Loma___Loma')
ScriptSimpleType.Lyci___Lycian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Lyci - Lycian', tag='Lyci___Lycian')
ScriptSimpleType.Lydi___Lydian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Lydi - Lydian', tag='Lydi___Lydian')
ScriptSimpleType.Mahj___Mahajani = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mahj - Mahajani', tag='Mahj___Mahajani')
ScriptSimpleType.Mand___Mandaic_Mandaean = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mand - Mandaic, Mandaean', tag='Mand___Mandaic_Mandaean')
ScriptSimpleType.Mani___Manichaean = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mani - Manichaean', tag='Mani___Manichaean')
ScriptSimpleType.Marc___Marchen = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Marc - Marchen', tag='Marc___Marchen')
ScriptSimpleType.Maya___Mayan_hieroglyphs = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Maya - Mayan hieroglyphs', tag='Maya___Mayan_hieroglyphs')
ScriptSimpleType.Mend___Mende_Kikakui = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mend - Mende Kikakui', tag='Mend___Mende_Kikakui')
ScriptSimpleType.Merc___Meroitic_Cursive = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Merc - Meroitic Cursive', tag='Merc___Meroitic_Cursive')
ScriptSimpleType.Mero___Meroitic_Hieroglyphs = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mero - Meroitic Hieroglyphs', tag='Mero___Meroitic_Hieroglyphs')
ScriptSimpleType.Mlym___Malayalam = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mlym - Malayalam', tag='Mlym___Malayalam')
ScriptSimpleType.Modi___Modi_Mo = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Modi - Modi, Moḍī', tag='Modi___Modi_Mo')
ScriptSimpleType.Mong___Mongolian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mong - Mongolian', tag='Mong___Mongolian')
ScriptSimpleType.Moon___Moon_Moon_code_Moon_script_Moon_type = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Moon - Moon (Moon code, Moon script, Moon type)', tag='Moon___Moon_Moon_code_Moon_script_Moon_type')
ScriptSimpleType.Mroo___Mro_Mru = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mroo - Mro, Mru', tag='Mroo___Mro_Mru')
ScriptSimpleType.Mtei___Meitei_Mayek_Meithei_Meetei = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mtei - Meitei Mayek (Meithei, Meetei)', tag='Mtei___Meitei_Mayek_Meithei_Meetei')
ScriptSimpleType.Mult___Multani = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mult - Multani', tag='Mult___Multani')
ScriptSimpleType.Mymr___Myanmar_Burmese = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Mymr - Myanmar (Burmese)', tag='Mymr___Myanmar_Burmese')
ScriptSimpleType.Narb___Old_North_Arabian_Ancient_North_Arabian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Narb - Old North Arabian (Ancient North Arabian)', tag='Narb___Old_North_Arabian_Ancient_North_Arabian')
ScriptSimpleType.Nbat___Nabataean = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Nbat - Nabataean', tag='Nbat___Nabataean')
ScriptSimpleType.Newa___Newa_Newar_Newari = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Newa - Newa, Newar, Newari', tag='Newa___Newa_Newar_Newari')
ScriptSimpleType.Nkgb___Nakhi_Geba = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Nkgb - Nakhi Geba', tag='Nkgb___Nakhi_Geba')
ScriptSimpleType.Nkoo___NKo = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Nkoo - N’Ko', tag='Nkoo___NKo')
ScriptSimpleType.Nshu___Nshu = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Nshu - Nüshu', tag='Nshu___Nshu')
ScriptSimpleType.Ogam___Ogham = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Ogam - Ogham', tag='Ogam___Ogham')
ScriptSimpleType.Olck___Ol_Chiki_Ol_Cemet_Ol_Santali = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Olck - Ol Chiki (Ol Cemet’, Ol, Santali)', tag='Olck___Ol_Chiki_Ol_Cemet_Ol_Santali')
ScriptSimpleType.Orkh___Old_Turkic_Orkhon_Runic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Orkh - Old Turkic, Orkhon Runic', tag='Orkh___Old_Turkic_Orkhon_Runic')
ScriptSimpleType.Orya___Oriya = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Orya - Oriya', tag='Orya___Oriya')
ScriptSimpleType.Osge___Osage = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Osge - Osage', tag='Osge___Osage')
ScriptSimpleType.Osma___Osmanya = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Osma - Osmanya', tag='Osma___Osmanya')
ScriptSimpleType.Palm___Palmyrene = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Palm - Palmyrene', tag='Palm___Palmyrene')
ScriptSimpleType.Pauc___Pau_Cin_Hau = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Pauc - Pau Cin Hau', tag='Pauc___Pau_Cin_Hau')
ScriptSimpleType.Perm___Old_Permic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Perm - Old Permic', tag='Perm___Old_Permic')
ScriptSimpleType.Phag___Phags_pa = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Phag - Phags-pa', tag='Phag___Phags_pa')
ScriptSimpleType.Phli___Inscriptional_Pahlavi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Phli - Inscriptional Pahlavi', tag='Phli___Inscriptional_Pahlavi')
ScriptSimpleType.Phlp___Psalter_Pahlavi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Phlp - Psalter Pahlavi', tag='Phlp___Psalter_Pahlavi')
ScriptSimpleType.Phlv___Book_Pahlavi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Phlv - Book Pahlavi', tag='Phlv___Book_Pahlavi')
ScriptSimpleType.Phnx___Phoenician = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Phnx - Phoenician', tag='Phnx___Phoenician')
ScriptSimpleType.Piqd___Klingon_KLI_pIqaD = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Piqd - Klingon (KLI pIqaD)', tag='Piqd___Klingon_KLI_pIqaD')
ScriptSimpleType.Plrd___Miao_Pollard = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Plrd - Miao (Pollard)', tag='Plrd___Miao_Pollard')
ScriptSimpleType.Prti___Inscriptional_Parthian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Prti - Inscriptional Parthian', tag='Prti___Inscriptional_Parthian')
ScriptSimpleType.Rjng___Rejang_Redjang_Kaganga = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Rjng - Rejang (Redjang, Kaganga)', tag='Rjng___Rejang_Redjang_Kaganga')
ScriptSimpleType.Roro___Rongorongo = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Roro - Rongorongo', tag='Roro___Rongorongo')
ScriptSimpleType.Runr___Runic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Runr - Runic', tag='Runr___Runic')
ScriptSimpleType.Samr___Samaritan = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Samr - Samaritan', tag='Samr___Samaritan')
ScriptSimpleType.Sara___Sarati = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sara - Sarati', tag='Sara___Sarati')
ScriptSimpleType.Sarb___Old_South_Arabian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sarb - Old South Arabian', tag='Sarb___Old_South_Arabian')
ScriptSimpleType.Saur___Saurashtra = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Saur - Saurashtra', tag='Saur___Saurashtra')
ScriptSimpleType.Sgnw___SignWriting = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sgnw - SignWriting', tag='Sgnw___SignWriting')
ScriptSimpleType.Shaw___Shavian_Shaw = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Shaw - Shavian (Shaw)', tag='Shaw___Shavian_Shaw')
ScriptSimpleType.Shrd___Sharada_rad = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Shrd - Sharada, Śāradā', tag='Shrd___Sharada_rad')
ScriptSimpleType.Sidd___Siddham = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sidd - Siddham', tag='Sidd___Siddham')
ScriptSimpleType.Sind___Khudawadi_Sindhi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sind - Khudawadi, Sindhi', tag='Sind___Khudawadi_Sindhi')
ScriptSimpleType.Sinh___Sinhala = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sinh - Sinhala', tag='Sinh___Sinhala')
ScriptSimpleType.Sora___Sora_Sompeng = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sora - Sora Sompeng', tag='Sora___Sora_Sompeng')
ScriptSimpleType.Sund___Sundanese = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sund - Sundanese', tag='Sund___Sundanese')
ScriptSimpleType.Sylo___Syloti_Nagri = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Sylo - Syloti Nagri', tag='Sylo___Syloti_Nagri')
ScriptSimpleType.Syrc___Syriac = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Syrc - Syriac', tag='Syrc___Syriac')
ScriptSimpleType.Syre___Syriac_Estrangelo_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Syre - Syriac (Estrangelo variant)', tag='Syre___Syriac_Estrangelo_variant')
ScriptSimpleType.Syrj___Syriac_Western_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Syrj - Syriac (Western variant)', tag='Syrj___Syriac_Western_variant')
ScriptSimpleType.Syrn___Syriac_Eastern_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Syrn - Syriac (Eastern variant)', tag='Syrn___Syriac_Eastern_variant')
ScriptSimpleType.Tagb___Tagbanwa = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tagb - Tagbanwa', tag='Tagb___Tagbanwa')
ScriptSimpleType.Takr___Takri = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Takr - Takri', tag='Takr___Takri')
ScriptSimpleType.Tale___Tai_Le = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tale - Tai Le', tag='Tale___Tai_Le')
ScriptSimpleType.Talu___New_Tai_Lue = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Talu - New Tai Lue', tag='Talu___New_Tai_Lue')
ScriptSimpleType.Taml___Tamil = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Taml - Tamil', tag='Taml___Tamil')
ScriptSimpleType.Tang___Tangut = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tang - Tangut', tag='Tang___Tangut')
ScriptSimpleType.Tavt___Tai_Viet = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tavt - Tai Viet', tag='Tavt___Tai_Viet')
ScriptSimpleType.Telu___Telugu = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Telu - Telugu', tag='Telu___Telugu')
ScriptSimpleType.Teng___Tengwar = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Teng - Tengwar', tag='Teng___Tengwar')
ScriptSimpleType.Tfng___Tifinagh_Berber = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tfng - Tifinagh (Berber)', tag='Tfng___Tifinagh_Berber')
ScriptSimpleType.Tglg___Tagalog_Baybayin_Alibata = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tglg - Tagalog (Baybayin, Alibata)', tag='Tglg___Tagalog_Baybayin_Alibata')
ScriptSimpleType.Thaa___Thaana = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Thaa - Thaana', tag='Thaa___Thaana')
ScriptSimpleType.Thai___Thai = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Thai - Thai', tag='Thai___Thai')
ScriptSimpleType.Tibt___Tibetan = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tibt - Tibetan', tag='Tibt___Tibetan')
ScriptSimpleType.Tirh___Tirhuta = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Tirh - Tirhuta', tag='Tirh___Tirhuta')
ScriptSimpleType.Ugar___Ugaritic = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Ugar - Ugaritic', tag='Ugar___Ugaritic')
ScriptSimpleType.Vaii___Vai = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Vaii - Vai', tag='Vaii___Vai')
ScriptSimpleType.Visp___Visible_Speech = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Visp - Visible Speech', tag='Visp___Visible_Speech')
ScriptSimpleType.Wara___Warang_Citi_Varang_Kshiti = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Wara - Warang Citi (Varang Kshiti)', tag='Wara___Warang_Citi_Varang_Kshiti')
ScriptSimpleType.Wole___Woleai = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Wole - Woleai', tag='Wole___Woleai')
ScriptSimpleType.Xpeo___Old_Persian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Xpeo - Old Persian', tag='Xpeo___Old_Persian')
ScriptSimpleType.Xsux___Cuneiform_Sumero_Akkadian = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Xsux - Cuneiform, Sumero-Akkadian', tag='Xsux___Cuneiform_Sumero_Akkadian')
ScriptSimpleType.Yiii___Yi = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Yiii - Yi', tag='Yiii___Yi')
ScriptSimpleType.Zinh___Code_for_inherited_script = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zinh - Code for inherited script', tag='Zinh___Code_for_inherited_script')
ScriptSimpleType.Zmth___Mathematical_notation = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zmth - Mathematical notation', tag='Zmth___Mathematical_notation')
ScriptSimpleType.Zsye___Symbols_Emoji_variant = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zsye - Symbols (Emoji variant)', tag='Zsye___Symbols_Emoji_variant')
ScriptSimpleType.Zsym___Symbols = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zsym - Symbols', tag='Zsym___Symbols')
ScriptSimpleType.Zxxx___Code_for_unwritten_documents = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zxxx - Code for unwritten documents', tag='Zxxx___Code_for_unwritten_documents')
ScriptSimpleType.Zyyy___Code_for_undetermined_script = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zyyy - Code for undetermined script', tag='Zyyy___Code_for_undetermined_script')
ScriptSimpleType.Zzzz___Code_for_uncoded_script = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='Zzzz - Code for uncoded script', tag='Zzzz___Code_for_uncoded_script')
ScriptSimpleType.other = ScriptSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
ScriptSimpleType._InitializeFacetMap(ScriptSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ScriptSimpleType', ScriptSimpleType)
_module_typeBindings.ScriptSimpleType = ScriptSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ColourDepthSimpleType
class ColourDepthSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ColourDepthSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1621, 4)
    _Documentation = None
ColourDepthSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ColourDepthSimpleType, enum_prefix=None)
ColourDepthSimpleType.bilevel = ColourDepthSimpleType._CF_enumeration.addEnumeration(unicode_value='bilevel', tag='bilevel')
ColourDepthSimpleType.greyscale = ColourDepthSimpleType._CF_enumeration.addEnumeration(unicode_value='greyscale', tag='greyscale')
ColourDepthSimpleType.colour = ColourDepthSimpleType._CF_enumeration.addEnumeration(unicode_value='colour', tag='colour')
ColourDepthSimpleType.other = ColourDepthSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
ColourDepthSimpleType._InitializeFacetMap(ColourDepthSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ColourDepthSimpleType', ColourDepthSimpleType)
_module_typeBindings.ColourDepthSimpleType = ColourDepthSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicsTypeSimpleType
class GraphicsTypeSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GraphicsTypeSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1629, 4)
    _Documentation = None
GraphicsTypeSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=GraphicsTypeSimpleType, enum_prefix=None)
GraphicsTypeSimpleType.logo = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='logo', tag='logo')
GraphicsTypeSimpleType.letterhead = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='letterhead', tag='letterhead')
GraphicsTypeSimpleType.decoration = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='decoration', tag='decoration')
GraphicsTypeSimpleType.frame = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='frame', tag='frame')
GraphicsTypeSimpleType.handwritten_annotation = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='handwritten-annotation', tag='handwritten_annotation')
GraphicsTypeSimpleType.stamp = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='stamp', tag='stamp')
GraphicsTypeSimpleType.signature = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='signature', tag='signature')
GraphicsTypeSimpleType.barcode = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='barcode', tag='barcode')
GraphicsTypeSimpleType.paper_grow = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='paper-grow', tag='paper_grow')
GraphicsTypeSimpleType.punch_hole = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='punch-hole', tag='punch_hole')
GraphicsTypeSimpleType.other = GraphicsTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
GraphicsTypeSimpleType._InitializeFacetMap(GraphicsTypeSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'GraphicsTypeSimpleType', GraphicsTypeSimpleType)
_module_typeBindings.GraphicsTypeSimpleType = GraphicsTypeSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartTypeSimpleType
class ChartTypeSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ChartTypeSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1644, 4)
    _Documentation = None
ChartTypeSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ChartTypeSimpleType, enum_prefix=None)
ChartTypeSimpleType.bar = ChartTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='bar', tag='bar')
ChartTypeSimpleType.line = ChartTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='line', tag='line')
ChartTypeSimpleType.pie = ChartTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='pie', tag='pie')
ChartTypeSimpleType.scatter = ChartTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='scatter', tag='scatter')
ChartTypeSimpleType.surface = ChartTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='surface', tag='surface')
ChartTypeSimpleType.other = ChartTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
ChartTypeSimpleType._InitializeFacetMap(ChartTypeSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ChartTypeSimpleType', ChartTypeSimpleType)
_module_typeBindings.ChartTypeSimpleType = ChartTypeSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PointsType
class PointsType (pyxb.binding.datatypes.string):

    """Point list with format "x1,y1 x2,y2 ..." """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PointsType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1684, 4)
    _Documentation = 'Point list with format "x1,y1 x2,y2 ..."'
PointsType._CF_pattern = pyxb.binding.facets.CF_pattern()
PointsType._CF_pattern.addPattern(pattern='([0-9]+,[0-9]+ )+([0-9]+,[0-9]+)')
PointsType._InitializeFacetMap(PointsType._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'PointsType', PointsType)
_module_typeBindings.PointsType = PointsType

# Atomic simple type: [anonymous]
class STD_ANON_2 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1731, 6)
    _Documentation = None
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2, enum_prefix=None)
STD_ANON_2.link = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='link', tag='link')
STD_ANON_2.join = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='join', tag='join')
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_enumeration)
_module_typeBindings.STD_ANON_2 = STD_ANON_2

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ProductionSimpleType
class ProductionSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Text production type"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProductionSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1744, 4)
    _Documentation = 'Text production type'
ProductionSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ProductionSimpleType, enum_prefix=None)
ProductionSimpleType.printed = ProductionSimpleType._CF_enumeration.addEnumeration(unicode_value='printed', tag='printed')
ProductionSimpleType.typewritten = ProductionSimpleType._CF_enumeration.addEnumeration(unicode_value='typewritten', tag='typewritten')
ProductionSimpleType.handwritten_cursive = ProductionSimpleType._CF_enumeration.addEnumeration(unicode_value='handwritten-cursive', tag='handwritten_cursive')
ProductionSimpleType.handwritten_printscript = ProductionSimpleType._CF_enumeration.addEnumeration(unicode_value='handwritten-printscript', tag='handwritten_printscript')
ProductionSimpleType.medieval_manuscript = ProductionSimpleType._CF_enumeration.addEnumeration(unicode_value='medieval-manuscript', tag='medieval_manuscript')
ProductionSimpleType.other = ProductionSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
ProductionSimpleType._InitializeFacetMap(ProductionSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ProductionSimpleType', ProductionSimpleType)
_module_typeBindings.ProductionSimpleType = ProductionSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AlignSimpleType
class AlignSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AlignSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1895, 4)
    _Documentation = None
AlignSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AlignSimpleType, enum_prefix=None)
AlignSimpleType.left = AlignSimpleType._CF_enumeration.addEnumeration(unicode_value='left', tag='left')
AlignSimpleType.centre = AlignSimpleType._CF_enumeration.addEnumeration(unicode_value='centre', tag='centre')
AlignSimpleType.right = AlignSimpleType._CF_enumeration.addEnumeration(unicode_value='right', tag='right')
AlignSimpleType.justify = AlignSimpleType._CF_enumeration.addEnumeration(unicode_value='justify', tag='justify')
AlignSimpleType._InitializeFacetMap(AlignSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'AlignSimpleType', AlignSimpleType)
_module_typeBindings.AlignSimpleType = AlignSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GroupTypeSimpleType
class GroupTypeSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GroupTypeSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1903, 4)
    _Documentation = None
GroupTypeSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=GroupTypeSimpleType, enum_prefix=None)
GroupTypeSimpleType.paragraph = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='paragraph', tag='paragraph')
GroupTypeSimpleType.list = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='list', tag='list')
GroupTypeSimpleType.list_item = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='list-item', tag='list_item')
GroupTypeSimpleType.figure = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='figure', tag='figure')
GroupTypeSimpleType.article = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='article', tag='article')
GroupTypeSimpleType.div = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='div', tag='div')
GroupTypeSimpleType.other = GroupTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
GroupTypeSimpleType._InitializeFacetMap(GroupTypeSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'GroupTypeSimpleType', GroupTypeSimpleType)
_module_typeBindings.GroupTypeSimpleType = GroupTypeSimpleType

# Atomic simple type: {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextDataTypeSimpleType
class TextDataTypeSimpleType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextDataTypeSimpleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1915, 4)
    _Documentation = None
TextDataTypeSimpleType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TextDataTypeSimpleType, enum_prefix=None)
TextDataTypeSimpleType.xsddecimal = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:decimal', tag='xsddecimal')
TextDataTypeSimpleType.xsdfloat = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:float', tag='xsdfloat')
TextDataTypeSimpleType.xsdinteger = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:integer', tag='xsdinteger')
TextDataTypeSimpleType.xsdboolean = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:boolean', tag='xsdboolean')
TextDataTypeSimpleType.xsddate = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:date', tag='xsddate')
TextDataTypeSimpleType.xsdtime = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:time', tag='xsdtime')
TextDataTypeSimpleType.xsddateTime = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:dateTime', tag='xsddateTime')
TextDataTypeSimpleType.xsdstring = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='xsd:string', tag='xsdstring')
TextDataTypeSimpleType.other = TextDataTypeSimpleType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
TextDataTypeSimpleType._InitializeFacetMap(TextDataTypeSimpleType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'TextDataTypeSimpleType', TextDataTypeSimpleType)
_module_typeBindings.TextDataTypeSimpleType = TextDataTypeSimpleType

# Atomic simple type: [anonymous]
class STD_ANON_3 (pyxb.binding.datatypes.int):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2021, 12)
    _Documentation = None
STD_ANON_3._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=STD_ANON_3, value=pyxb.binding.datatypes.int(0))
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_minInclusive)
_module_typeBindings.STD_ANON_3 = STD_ANON_3

# Atomic simple type: [anonymous]
class STD_ANON_4 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2032, 12)
    _Documentation = None
STD_ANON_4._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_4, enum_prefix=None)
STD_ANON_4.base = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value='base', tag='base')
STD_ANON_4.combining = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value='combining', tag='combining')
STD_ANON_4._InitializeFacetMap(STD_ANON_4._CF_enumeration)
_module_typeBindings.STD_ANON_4 = STD_ANON_4

# Atomic simple type: [anonymous]
class STD_ANON_5 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2098, 6)
    _Documentation = None
STD_ANON_5._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_5, enum_prefix=None)
STD_ANON_5.xsdstring = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value='xsd:string', tag='xsdstring')
STD_ANON_5.xsdinteger = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value='xsd:integer', tag='xsdinteger')
STD_ANON_5.xsdboolean = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value='xsd:boolean', tag='xsdboolean')
STD_ANON_5.xsdfloat = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value='xsd:float', tag='xsdfloat')
STD_ANON_5._InitializeFacetMap(STD_ANON_5._CF_enumeration)
_module_typeBindings.STD_ANON_5 = STD_ANON_5

# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PcGtsType with content type ELEMENT_ONLY
class PcGtsType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PcGtsType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PcGtsType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 10, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Metadata uses Python identifier Metadata
    __Metadata = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Metadata'), 'Metadata', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PcGtsType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Metadata', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 12, 3), )

    
    Metadata = property(__Metadata.value, __Metadata.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Page uses Python identifier Page
    __Page = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Page'), 'Page', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PcGtsType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Page', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 13, 3), )

    
    Page = property(__Page.value, __Page.set, None, None)

    
    # Attribute pcGtsId uses Python identifier pcGtsId
    __pcGtsId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'pcGtsId'), 'pcGtsId', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PcGtsType_pcGtsId', pyxb.binding.datatypes.ID)
    __pcGtsId._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 15, 2)
    __pcGtsId._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 15, 2)
    
    pcGtsId = property(__pcGtsId.value, __pcGtsId.set, None, None)

    _ElementMap.update({
        __Metadata.name() : __Metadata,
        __Page.name() : __Page
    })
    _AttributeMap.update({
        __pcGtsId.name() : __pcGtsId
    })
_module_typeBindings.PcGtsType = PcGtsType
Namespace.addCategoryObject('typeBinding', 'PcGtsType', PcGtsType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MetadataType with content type ELEMENT_ONLY
class MetadataType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MetadataType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'MetadataType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 17, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Creator uses Python identifier Creator
    __Creator = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Creator'), 'Creator', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MetadataType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Creator', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 19, 3), )

    
    Creator = property(__Creator.value, __Creator.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Created uses Python identifier Created
    __Created = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Created'), 'Created', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MetadataType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Created', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 20, 3), )

    
    Created = property(__Created.value, __Created.set, None, '\n\t\t\t\t\t\tThe timestamp has to be in UTC (Coordinated\n\t\t\t\t\t\tUniversal Time) and not local time.\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LastChange uses Python identifier LastChange
    __LastChange = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'LastChange'), 'LastChange', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MetadataType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15LastChange', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 28, 3), )

    
    LastChange = property(__LastChange.value, __LastChange.set, None, '\n\t\t\t\t\t\tThe timestamp has to be in UTC (Coordinated\n\t\t\t\t\t\tUniversal Time) and not local time.\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Comments uses Python identifier Comments
    __Comments = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Comments'), 'Comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MetadataType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Comments', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 36, 3), )

    
    Comments = property(__Comments.value, __Comments.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MetadataType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 39, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Attribute externalRef uses Python identifier externalRef
    __externalRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'externalRef'), 'externalRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MetadataType_externalRef', pyxb.binding.datatypes.string)
    __externalRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 41, 2)
    __externalRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 41, 2)
    
    externalRef = property(__externalRef.value, __externalRef.set, None, 'External reference of any kind')

    _ElementMap.update({
        __Creator.name() : __Creator,
        __Created.name() : __Created,
        __LastChange.name() : __LastChange,
        __Comments.name() : __Comments,
        __UserDefined.name() : __UserDefined
    })
    _AttributeMap.update({
        __externalRef.name() : __externalRef
    })
_module_typeBindings.MetadataType = MetadataType
Namespace.addCategoryObject('typeBinding', 'MetadataType', MetadataType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PrintSpaceType with content type ELEMENT_ONLY
class PrintSpaceType (pyxb.binding.basis.complexTypeDefinition):
    """Determines the effective area on the paper of a printed page. Its size is equal for all pages of a book (exceptions: titlepage, multipage pictures).
It contains all living elements (except marginals) like body type, footnotes, headings, running titles.
It does not contain pagenumber (if not part of running title), marginals, signature mark, preview words.
"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PrintSpaceType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 965, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PrintSpaceType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 973, 3), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    _ElementMap.update({
        __Coords.name() : __Coords
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PrintSpaceType = PrintSpaceType
Namespace.addCategoryObject('typeBinding', 'PrintSpaceType', PrintSpaceType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ReadingOrderType with content type ELEMENT_ONLY
class ReadingOrderType (pyxb.binding.basis.complexTypeDefinition):
    """Definition of the reading order within the page. To express a reading order between elements they have to be included in an OrderedGroup. Groups may contain further groups."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ReadingOrderType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 977, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroup uses Python identifier OrderedGroup
    __OrderedGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup'), 'OrderedGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ReadingOrderType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15OrderedGroup', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 982, 12), )

    
    OrderedGroup = property(__OrderedGroup.value, __OrderedGroup.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroup uses Python identifier UnorderedGroup
    __UnorderedGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup'), 'UnorderedGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ReadingOrderType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnorderedGroup', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 983, 12), )

    
    UnorderedGroup = property(__UnorderedGroup.value, __UnorderedGroup.set, None, None)

    _ElementMap.update({
        __OrderedGroup.name() : __OrderedGroup,
        __UnorderedGroup.name() : __UnorderedGroup
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ReadingOrderType = ReadingOrderType
Namespace.addCategoryObject('typeBinding', 'ReadingOrderType', ReadingOrderType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRefIndexedType with content type EMPTY
class RegionRefIndexedType (pyxb.binding.basis.complexTypeDefinition):
    """Numbered region"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexedType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 987, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'index'), 'index', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionRefIndexedType_index', pyxb.binding.datatypes.int, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 991, 8)
    __index._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 991, 8)
    
    index = property(__index.value, __index.set, None, 'Position (order number) of this item within the current hierarchy level.')

    
    # Attribute regionRef uses Python identifier regionRef
    __regionRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'regionRef'), 'regionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionRefIndexedType_regionRef', pyxb.binding.datatypes.IDREF, required=True)
    __regionRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 995, 8)
    __regionRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 995, 8)
    
    regionRef = property(__regionRef.value, __regionRef.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __index.name() : __index,
        __regionRef.name() : __regionRef
    })
_module_typeBindings.RegionRefIndexedType = RegionRefIndexedType
Namespace.addCategoryObject('typeBinding', 'RegionRefIndexedType', RegionRefIndexedType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRefType with content type EMPTY
class RegionRefType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRefType with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RegionRefType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1088, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute regionRef uses Python identifier regionRef
    __regionRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'regionRef'), 'regionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionRefType_regionRef', pyxb.binding.datatypes.IDREF, required=True)
    __regionRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1089, 2)
    __regionRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1089, 2)
    
    regionRef = property(__regionRef.value, __regionRef.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __regionRef.name() : __regionRef
    })
_module_typeBindings.RegionRefType = RegionRefType
Namespace.addCategoryObject('typeBinding', 'RegionRefType', RegionRefType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}BorderType with content type ELEMENT_ONLY
class BorderType (pyxb.binding.basis.complexTypeDefinition):
    """Border of the actual page (if the scanned image contains parts not belonging to the page)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BorderType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1161, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_BorderType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1166, 3), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    _ElementMap.update({
        __Coords.name() : __Coords
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.BorderType = BorderType
Namespace.addCategoryObject('typeBinding', 'BorderType', BorderType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LayersType with content type ELEMENT_ONLY
class LayersType (pyxb.binding.basis.complexTypeDefinition):
    """
    			Can be used to express the z-index of overlapping
    			regions. An element with a greater z-index is always in
    			front of another element with lower z-index.
    		"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LayersType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1655, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Layer uses Python identifier Layer
    __Layer = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Layer'), 'Layer', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LayersType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Layer', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1664, 6), )

    
    Layer = property(__Layer.value, __Layer.set, None, None)

    _ElementMap.update({
        __Layer.name() : __Layer
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.LayersType = LayersType
Namespace.addCategoryObject('typeBinding', 'LayersType', LayersType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LayerType with content type ELEMENT_ONLY
class LayerType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LayerType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LayerType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1669, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRef uses Python identifier RegionRef
    __RegionRef = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), 'RegionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LayerType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15RegionRef', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1671, 6), )

    
    RegionRef = property(__RegionRef.value, __RegionRef.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LayerType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1673, 5)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1673, 5)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute zIndex uses Python identifier zIndex
    __zIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'zIndex'), 'zIndex', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LayerType_zIndex', pyxb.binding.datatypes.int, required=True)
    __zIndex._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1674, 5)
    __zIndex._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1674, 5)
    
    zIndex = property(__zIndex.value, __zIndex.set, None, None)

    
    # Attribute caption uses Python identifier caption
    __caption = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'caption'), 'caption', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LayerType_caption', pyxb.binding.datatypes.string)
    __caption._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1675, 5)
    __caption._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1675, 5)
    
    caption = property(__caption.value, __caption.set, None, None)

    _ElementMap.update({
        __RegionRef.name() : __RegionRef
    })
    _AttributeMap.update({
        __id.name() : __id,
        __zIndex.name() : __zIndex,
        __caption.name() : __caption
    })
_module_typeBindings.LayerType = LayerType
Namespace.addCategoryObject('typeBinding', 'LayerType', LayerType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RelationsType with content type ELEMENT_ONLY
class RelationsType (pyxb.binding.basis.complexTypeDefinition):
    """
    			Container for one-to-one relations between layout
    			objects (for example: DropCap - paragraph, caption -
    			image)
    		"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RelationsType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1693, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Relation uses Python identifier Relation
    __Relation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Relation'), 'Relation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RelationsType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Relation', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1702, 6), )

    
    Relation = property(__Relation.value, __Relation.set, None, None)

    _ElementMap.update({
        __Relation.name() : __Relation
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.RelationsType = RelationsType
Namespace.addCategoryObject('typeBinding', 'RelationsType', RelationsType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType with content type ELEMENT_ONLY
class RegionType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1836, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles uses Python identifier Roles
    __Roles = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Roles'), 'Roles', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Roles', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6), )

    
    Roles = property(__Roles.value, __Roles.set, None, '\n    \t\t\t\t\tRoles the region takes (e.g. in context of a\n    \t\t\t\t\tparent region)\n    \t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion uses Python identifier TextRegion
    __TextRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextRegion'), 'TextRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7), )

    
    TextRegion = property(__TextRegion.value, __TextRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion uses Python identifier ImageRegion
    __ImageRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion'), 'ImageRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ImageRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7), )

    
    ImageRegion = property(__ImageRegion.value, __ImageRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion uses Python identifier LineDrawingRegion
    __LineDrawingRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion'), 'LineDrawingRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15LineDrawingRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7), )

    
    LineDrawingRegion = property(__LineDrawingRegion.value, __LineDrawingRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion uses Python identifier GraphicRegion
    __GraphicRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion'), 'GraphicRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15GraphicRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7), )

    
    GraphicRegion = property(__GraphicRegion.value, __GraphicRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion uses Python identifier TableRegion
    __TableRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TableRegion'), 'TableRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TableRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7), )

    
    TableRegion = property(__TableRegion.value, __TableRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion uses Python identifier ChartRegion
    __ChartRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion'), 'ChartRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ChartRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7), )

    
    ChartRegion = property(__ChartRegion.value, __ChartRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion uses Python identifier SeparatorRegion
    __SeparatorRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion'), 'SeparatorRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15SeparatorRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7), )

    
    SeparatorRegion = property(__SeparatorRegion.value, __SeparatorRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion uses Python identifier MathsRegion
    __MathsRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion'), 'MathsRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15MathsRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7), )

    
    MathsRegion = property(__MathsRegion.value, __MathsRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion uses Python identifier ChemRegion
    __ChemRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion'), 'ChemRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ChemRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7), )

    
    ChemRegion = property(__ChemRegion.value, __ChemRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion uses Python identifier MusicRegion
    __MusicRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion'), 'MusicRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15MusicRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7), )

    
    MusicRegion = property(__MusicRegion.value, __MusicRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion uses Python identifier AdvertRegion
    __AdvertRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion'), 'AdvertRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15AdvertRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7), )

    
    AdvertRegion = property(__AdvertRegion.value, __AdvertRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion uses Python identifier NoiseRegion
    __NoiseRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion'), 'NoiseRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15NoiseRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7), )

    
    NoiseRegion = property(__NoiseRegion.value, __NoiseRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion uses Python identifier UnknownRegion
    __UnknownRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion'), 'UnknownRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnknownRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7), )

    
    UnknownRegion = property(__UnknownRegion.value, __UnknownRegion.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1877, 5)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1877, 5)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1878, 5)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1878, 5)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1883, 5)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1883, 5)
    
    comments = property(__comments.value, __comments.set, None, None)

    
    # Attribute continuation uses Python identifier continuation
    __continuation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'continuation'), 'continuation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RegionType_continuation', pyxb.binding.datatypes.boolean)
    __continuation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1884, 5)
    __continuation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1884, 5)
    
    continuation = property(__continuation.value, __continuation.set, None, 'Is this region a continuation of another region (in previous column or page, for example)?')

    _ElementMap.update({
        __Coords.name() : __Coords,
        __UserDefined.name() : __UserDefined,
        __Roles.name() : __Roles,
        __TextRegion.name() : __TextRegion,
        __ImageRegion.name() : __ImageRegion,
        __LineDrawingRegion.name() : __LineDrawingRegion,
        __GraphicRegion.name() : __GraphicRegion,
        __TableRegion.name() : __TableRegion,
        __ChartRegion.name() : __ChartRegion,
        __SeparatorRegion.name() : __SeparatorRegion,
        __MathsRegion.name() : __MathsRegion,
        __ChemRegion.name() : __ChemRegion,
        __MusicRegion.name() : __MusicRegion,
        __AdvertRegion.name() : __AdvertRegion,
        __NoiseRegion.name() : __NoiseRegion,
        __UnknownRegion.name() : __UnknownRegion
    })
    _AttributeMap.update({
        __id.name() : __id,
        __custom.name() : __custom,
        __comments.name() : __comments,
        __continuation.name() : __continuation
    })
_module_typeBindings.RegionType = RegionType
Namespace.addCategoryObject('typeBinding', 'RegionType', RegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AlternativeImageType with content type EMPTY
class AlternativeImageType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AlternativeImageType with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AlternativeImageType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1890, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute filename uses Python identifier filename
    __filename = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'filename'), 'filename', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_AlternativeImageType_filename', pyxb.binding.datatypes.string, required=True)
    __filename._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1891, 5)
    __filename._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1891, 5)
    
    filename = property(__filename.value, __filename.set, None, None)

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_AlternativeImageType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1892, 5)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1892, 5)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __filename.name() : __filename,
        __comments.name() : __comments
    })
_module_typeBindings.AlternativeImageType = AlternativeImageType
Namespace.addCategoryObject('typeBinding', 'AlternativeImageType', AlternativeImageType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemesType with content type ELEMENT_ONLY
class GraphemesType (pyxb.binding.basis.complexTypeDefinition):
    """
    			Container for graphemes, grapheme groups and
    			non-printing characters
    		"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GraphemesType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1993, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Grapheme uses Python identifier Grapheme
    __Grapheme = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Grapheme'), 'Grapheme', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemesType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Grapheme', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2001, 6), )

    
    Grapheme = property(__Grapheme.value, __Grapheme.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NonPrintingChar uses Python identifier NonPrintingChar
    __NonPrintingChar = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'NonPrintingChar'), 'NonPrintingChar', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemesType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15NonPrintingChar', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2002, 6), )

    
    NonPrintingChar = property(__NonPrintingChar.value, __NonPrintingChar.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeGroup uses Python identifier GraphemeGroup
    __GraphemeGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'GraphemeGroup'), 'GraphemeGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemesType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15GraphemeGroup', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2003, 6), )

    
    GraphemeGroup = property(__GraphemeGroup.value, __GraphemeGroup.set, None, None)

    _ElementMap.update({
        __Grapheme.name() : __Grapheme,
        __NonPrintingChar.name() : __NonPrintingChar,
        __GraphemeGroup.name() : __GraphemeGroup
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.GraphemesType = GraphemesType
Namespace.addCategoryObject('typeBinding', 'GraphemesType', GraphemesType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefinedType with content type ELEMENT_ONLY
class UserDefinedType (pyxb.binding.basis.complexTypeDefinition):
    """Container for user-defined attributes"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UserDefinedType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2082, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserAttribute uses Python identifier UserAttribute
    __UserAttribute = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserAttribute'), 'UserAttribute', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UserDefinedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserAttribute', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2087, 6), )

    
    UserAttribute = property(__UserAttribute.value, __UserAttribute.set, None, None)

    _ElementMap.update({
        __UserAttribute.name() : __UserAttribute
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.UserDefinedType = UserDefinedType
Namespace.addCategoryObject('typeBinding', 'UserDefinedType', UserDefinedType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableCellRoleType with content type EMPTY
class TableCellRoleType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableCellRoleType with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TableCellRoleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2110, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute rowIndex uses Python identifier rowIndex
    __rowIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'rowIndex'), 'rowIndex', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableCellRoleType_rowIndex', pyxb.binding.datatypes.int, required=True)
    __rowIndex._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2111, 5)
    __rowIndex._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2111, 5)
    
    rowIndex = property(__rowIndex.value, __rowIndex.set, None, 'Cell position in table starting with row 0')

    
    # Attribute columnIndex uses Python identifier columnIndex
    __columnIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'columnIndex'), 'columnIndex', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableCellRoleType_columnIndex', pyxb.binding.datatypes.int, required=True)
    __columnIndex._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2115, 5)
    __columnIndex._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2115, 5)
    
    columnIndex = property(__columnIndex.value, __columnIndex.set, None, 'Cell position in table starting with column 0')

    
    # Attribute rowSpan uses Python identifier rowSpan
    __rowSpan = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'rowSpan'), 'rowSpan', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableCellRoleType_rowSpan', pyxb.binding.datatypes.int)
    __rowSpan._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2119, 5)
    __rowSpan._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2119, 5)
    
    rowSpan = property(__rowSpan.value, __rowSpan.set, None, 'Number of rows the cell spans (optional; default is 1)')

    
    # Attribute colSpan uses Python identifier colSpan
    __colSpan = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'colSpan'), 'colSpan', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableCellRoleType_colSpan', pyxb.binding.datatypes.int)
    __colSpan._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2123, 5)
    __colSpan._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2123, 5)
    
    colSpan = property(__colSpan.value, __colSpan.set, None, 'Number of columns the cell spans (optional; default is 1)')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __rowIndex.name() : __rowIndex,
        __columnIndex.name() : __columnIndex,
        __rowSpan.name() : __rowSpan,
        __colSpan.name() : __colSpan
    })
_module_typeBindings.TableCellRoleType = TableCellRoleType
Namespace.addCategoryObject('typeBinding', 'TableCellRoleType', TableCellRoleType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RolesType with content type ELEMENT_ONLY
class RolesType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RolesType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RolesType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2129, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableCellRole uses Python identifier TableCellRole
    __TableCellRole = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TableCellRole'), 'TableCellRole', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RolesType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TableCellRole', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2131, 12), )

    
    TableCellRole = property(__TableCellRole.value, __TableCellRole.set, None, 'Data for a region that takes on the role of a table cell within a parent table region')

    _ElementMap.update({
        __TableCellRole.name() : __TableCellRole
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.RolesType = RolesType
Namespace.addCategoryObject('typeBinding', 'RolesType', RolesType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PageType with content type ELEMENT_ONLY
class PageType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PageType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PageType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 46, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AlternativeImage uses Python identifier AlternativeImage
    __AlternativeImage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'AlternativeImage'), 'AlternativeImage', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15AlternativeImage', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 48, 3), )

    
    AlternativeImage = property(__AlternativeImage.value, __AlternativeImage.set, None, '\n\t\t\t\t\t\tAlternative document page images (e.g.\n\t\t\t\t\t\tblack-and-white)\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Border uses Python identifier Border
    __Border = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Border'), 'Border', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Border', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 58, 3), )

    
    Border = property(__Border.value, __Border.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PrintSpace uses Python identifier PrintSpace
    __PrintSpace = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'PrintSpace'), 'PrintSpace', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15PrintSpace', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 61, 3), )

    
    PrintSpace = property(__PrintSpace.value, __PrintSpace.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ReadingOrder uses Python identifier ReadingOrder
    __ReadingOrder = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ReadingOrder'), 'ReadingOrder', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ReadingOrder', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 64, 3), )

    
    ReadingOrder = property(__ReadingOrder.value, __ReadingOrder.set, None, '')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Layers uses Python identifier Layers
    __Layers = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Layers'), 'Layers', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Layers', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 70, 3), )

    
    Layers = property(__Layers.value, __Layers.set, None, '\n\t\t\t\t\t\tUnassigned regions are considered to be in the\n\t\t\t\t\t\t(virtual) default layer which is to be treated\n\t\t\t\t\t\tas below any other layers.\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Relations uses Python identifier Relations
    __Relations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Relations'), 'Relations', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Relations', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 80, 3), )

    
    Relations = property(__Relations.value, __Relations.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 83, 12), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion uses Python identifier TextRegion
    __TextRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextRegion'), 'TextRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 85, 4), )

    
    TextRegion = property(__TextRegion.value, __TextRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion uses Python identifier ImageRegion
    __ImageRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion'), 'ImageRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ImageRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 86, 4), )

    
    ImageRegion = property(__ImageRegion.value, __ImageRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion uses Python identifier LineDrawingRegion
    __LineDrawingRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion'), 'LineDrawingRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15LineDrawingRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 88, 4), )

    
    LineDrawingRegion = property(__LineDrawingRegion.value, __LineDrawingRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion uses Python identifier GraphicRegion
    __GraphicRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion'), 'GraphicRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15GraphicRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 91, 4), )

    
    GraphicRegion = property(__GraphicRegion.value, __GraphicRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion uses Python identifier TableRegion
    __TableRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TableRegion'), 'TableRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TableRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 94, 4), )

    
    TableRegion = property(__TableRegion.value, __TableRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion uses Python identifier ChartRegion
    __ChartRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion'), 'ChartRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ChartRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 96, 4), )

    
    ChartRegion = property(__ChartRegion.value, __ChartRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion uses Python identifier SeparatorRegion
    __SeparatorRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion'), 'SeparatorRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15SeparatorRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 98, 4), )

    
    SeparatorRegion = property(__SeparatorRegion.value, __SeparatorRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion uses Python identifier MathsRegion
    __MathsRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion'), 'MathsRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15MathsRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 101, 4), )

    
    MathsRegion = property(__MathsRegion.value, __MathsRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion uses Python identifier ChemRegion
    __ChemRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion'), 'ChemRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15ChemRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 103, 4), )

    
    ChemRegion = property(__ChemRegion.value, __ChemRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion uses Python identifier MusicRegion
    __MusicRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion'), 'MusicRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15MusicRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 104, 4), )

    
    MusicRegion = property(__MusicRegion.value, __MusicRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion uses Python identifier AdvertRegion
    __AdvertRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion'), 'AdvertRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15AdvertRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 105, 4), )

    
    AdvertRegion = property(__AdvertRegion.value, __AdvertRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion uses Python identifier NoiseRegion
    __NoiseRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion'), 'NoiseRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15NoiseRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 108, 4), )

    
    NoiseRegion = property(__NoiseRegion.value, __NoiseRegion.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion uses Python identifier UnknownRegion
    __UnknownRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion'), 'UnknownRegion', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnknownRegion', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 110, 4), )

    
    UnknownRegion = property(__UnknownRegion.value, __UnknownRegion.set, None, None)

    
    # Attribute imageFilename uses Python identifier imageFilename
    __imageFilename = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'imageFilename'), 'imageFilename', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_imageFilename', pyxb.binding.datatypes.string, required=True)
    __imageFilename._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 116, 2)
    __imageFilename._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 116, 2)
    
    imageFilename = property(__imageFilename.value, __imageFilename.set, None, None)

    
    # Attribute imageWidth uses Python identifier imageWidth
    __imageWidth = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'imageWidth'), 'imageWidth', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_imageWidth', pyxb.binding.datatypes.int, required=True)
    __imageWidth._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 117, 2)
    __imageWidth._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 117, 2)
    
    imageWidth = property(__imageWidth.value, __imageWidth.set, None, None)

    
    # Attribute imageHeight uses Python identifier imageHeight
    __imageHeight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'imageHeight'), 'imageHeight', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_imageHeight', pyxb.binding.datatypes.int, required=True)
    __imageHeight._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 118, 2)
    __imageHeight._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 118, 2)
    
    imageHeight = property(__imageHeight.value, __imageHeight.set, None, None)

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 119, 2)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 119, 2)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_type', _module_typeBindings.PageTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 124, 2)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 124, 2)
    
    type = property(__type.value, __type.set, None, 'Page type')

    
    # Attribute primaryLanguage uses Python identifier primaryLanguage
    __primaryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryLanguage'), 'primaryLanguage', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_primaryLanguage', _module_typeBindings.LanguageSimpleType)
    __primaryLanguage._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 129, 2)
    __primaryLanguage._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 129, 2)
    
    primaryLanguage = property(__primaryLanguage.value, __primaryLanguage.set, None, '\n\t\t\t\t\tThe primary language used in the page (lower-level definitions override the page-level definition)\n\t\t\t\t')

    
    # Attribute secondaryLanguage uses Python identifier secondaryLanguage
    __secondaryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'secondaryLanguage'), 'secondaryLanguage', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_secondaryLanguage', _module_typeBindings.LanguageSimpleType)
    __secondaryLanguage._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 137, 2)
    __secondaryLanguage._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 137, 2)
    
    secondaryLanguage = property(__secondaryLanguage.value, __secondaryLanguage.set, None, '\n\t\t\t\t\tThe secondary language used in the page (lower-level definitions override the page-level definition)\n\t\t\t\t')

    
    # Attribute primaryScript uses Python identifier primaryScript
    __primaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryScript'), 'primaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_primaryScript', _module_typeBindings.ScriptSimpleType)
    __primaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 145, 2)
    __primaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 145, 2)
    
    primaryScript = property(__primaryScript.value, __primaryScript.set, None, '\n\t\t\t\t\tThe primary script used in the page (lower-level definitions override the page-level definition)\n\t\t\t\t')

    
    # Attribute secondaryScript uses Python identifier secondaryScript
    __secondaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'secondaryScript'), 'secondaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_secondaryScript', _module_typeBindings.ScriptSimpleType)
    __secondaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 153, 2)
    __secondaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 153, 2)
    
    secondaryScript = property(__secondaryScript.value, __secondaryScript.set, None, '\n\t\t\t\t\tThe secondary script used in the page (lower-level definitions override the page-level definition)\n\t\t\t\t')

    
    # Attribute readingDirection uses Python identifier readingDirection
    __readingDirection = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'readingDirection'), 'readingDirection', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_readingDirection', _module_typeBindings.ReadingDirectionSimpleType)
    __readingDirection._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 161, 2)
    __readingDirection._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 161, 2)
    
    readingDirection = property(__readingDirection.value, __readingDirection.set, None, '\n\t\t\t\t\tThe direction in which text in a region should be\n\t\t\t\t\tread (within lines) (lower-level definitions override the page-level definition)\n\t\t\t\t')

    
    # Attribute textLineOrder uses Python identifier textLineOrder
    __textLineOrder = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'textLineOrder'), 'textLineOrder', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_PageType_textLineOrder', _module_typeBindings.TextLineOrderSimpleType)
    __textLineOrder._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 170, 2)
    __textLineOrder._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 170, 2)
    
    textLineOrder = property(__textLineOrder.value, __textLineOrder.set, None, 'Inner-block order of text lines (in addition to “readingDirection” which is the inner-text line order of words and characters) (lower-level definitions override the page-level definition)')

    _ElementMap.update({
        __AlternativeImage.name() : __AlternativeImage,
        __Border.name() : __Border,
        __PrintSpace.name() : __PrintSpace,
        __ReadingOrder.name() : __ReadingOrder,
        __Layers.name() : __Layers,
        __Relations.name() : __Relations,
        __UserDefined.name() : __UserDefined,
        __TextRegion.name() : __TextRegion,
        __ImageRegion.name() : __ImageRegion,
        __LineDrawingRegion.name() : __LineDrawingRegion,
        __GraphicRegion.name() : __GraphicRegion,
        __TableRegion.name() : __TableRegion,
        __ChartRegion.name() : __ChartRegion,
        __SeparatorRegion.name() : __SeparatorRegion,
        __MathsRegion.name() : __MathsRegion,
        __ChemRegion.name() : __ChemRegion,
        __MusicRegion.name() : __MusicRegion,
        __AdvertRegion.name() : __AdvertRegion,
        __NoiseRegion.name() : __NoiseRegion,
        __UnknownRegion.name() : __UnknownRegion
    })
    _AttributeMap.update({
        __imageFilename.name() : __imageFilename,
        __imageWidth.name() : __imageWidth,
        __imageHeight.name() : __imageHeight,
        __custom.name() : __custom,
        __type.name() : __type,
        __primaryLanguage.name() : __primaryLanguage,
        __secondaryLanguage.name() : __secondaryLanguage,
        __primaryScript.name() : __primaryScript,
        __secondaryScript.name() : __secondaryScript,
        __readingDirection.name() : __readingDirection,
        __textLineOrder.name() : __textLineOrder
    })
_module_typeBindings.PageType = PageType
Namespace.addCategoryObject('typeBinding', 'PageType', PageType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegionType with content type ELEMENT_ONLY
class TextRegionType (RegionType):
    """
				Pure text is represented as a text region. This includes
				drop capitals, but practically ornate text may be
				considered as a graphic.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 177, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextLine uses Python identifier TextLine
    __TextLine = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextLine'), 'TextLine', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextLine', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 188, 4), )

    
    TextLine = property(__TextLine.value, __TextLine.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv uses Python identifier TextEquiv
    __TextEquiv = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), 'TextEquiv', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextEquiv', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 191, 4), )

    
    TextEquiv = property(__TextEquiv.value, __TextEquiv.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextStyle uses Python identifier TextStyle
    __TextStyle = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), 'TextStyle', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextStyle', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 194, 4), )

    
    TextStyle = property(__TextStyle.value, __TextStyle.set, None, None)

    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 198, 3)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 198, 3)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_type', _module_typeBindings.TextTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 204, 3)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 204, 3)
    
    type = property(__type.value, __type.set, None, '\n\t\t\t\t\t\tThe nature of the text in the region\n\t\t\t\t\t')

    
    # Attribute leading uses Python identifier leading
    __leading = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'leading'), 'leading', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_leading', pyxb.binding.datatypes.int)
    __leading._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 212, 3)
    __leading._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 212, 3)
    
    leading = property(__leading.value, __leading.set, None, '\n\t\t\t\t\t\tThe degree of space in points between the lines of\n\t\t\t\t\t\ttext (line spacing)\n\t\t\t\t\t')

    
    # Attribute readingDirection uses Python identifier readingDirection
    __readingDirection = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'readingDirection'), 'readingDirection', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_readingDirection', _module_typeBindings.ReadingDirectionSimpleType)
    __readingDirection._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 220, 3)
    __readingDirection._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 220, 3)
    
    readingDirection = property(__readingDirection.value, __readingDirection.set, None, '\n\t\t\t\t\t\tThe direction in which text in a region should be\n\t\t\t\t\t\tread (within lines)\n\t\t\t\t\t')

    
    # Attribute textLineOrder uses Python identifier textLineOrder
    __textLineOrder = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'textLineOrder'), 'textLineOrder', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_textLineOrder', _module_typeBindings.TextLineOrderSimpleType)
    __textLineOrder._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 229, 3)
    __textLineOrder._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 229, 3)
    
    textLineOrder = property(__textLineOrder.value, __textLineOrder.set, None, 'Inner-block order of text lines (in addition to “readingDirection” which is the inner-text line order of words and characters)')

    
    # Attribute readingOrientation uses Python identifier readingOrientation
    __readingOrientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'readingOrientation'), 'readingOrientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_readingOrientation', pyxb.binding.datatypes.float)
    __readingOrientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 235, 3)
    __readingOrientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 235, 3)
    
    readingOrientation = property(__readingOrientation.value, __readingOrientation.set, None, 'The angle the baseline of text withing a region has to be rotated (relative to the rectangle encapsulating the region) in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute indented uses Python identifier indented
    __indented = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'indented'), 'indented', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_indented', pyxb.binding.datatypes.boolean)
    __indented._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 242, 3)
    __indented._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 242, 3)
    
    indented = property(__indented.value, __indented.set, None, '\n\t\t\t\t\t\tDefines whether a region of text is indented or not\n\t\t\t\t\t')

    
    # Attribute align uses Python identifier align
    __align = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'align'), 'align', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_align', _module_typeBindings.AlignSimpleType)
    __align._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 249, 3)
    __align._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 249, 3)
    
    align = property(__align.value, __align.set, None, 'Text align')

    
    # Attribute primaryLanguage uses Python identifier primaryLanguage
    __primaryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryLanguage'), 'primaryLanguage', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_primaryLanguage', _module_typeBindings.LanguageSimpleType)
    __primaryLanguage._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 254, 3)
    __primaryLanguage._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 254, 3)
    
    primaryLanguage = property(__primaryLanguage.value, __primaryLanguage.set, None, '\n\t\t\t\t\t\tThe primary language used in the region\n\t\t\t\t\t')

    
    # Attribute secondaryLanguage uses Python identifier secondaryLanguage
    __secondaryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'secondaryLanguage'), 'secondaryLanguage', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_secondaryLanguage', _module_typeBindings.LanguageSimpleType)
    __secondaryLanguage._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 262, 3)
    __secondaryLanguage._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 262, 3)
    
    secondaryLanguage = property(__secondaryLanguage.value, __secondaryLanguage.set, None, '\n\t\t\t\t\t\tThe secondary language used in the region\n\t\t\t\t\t')

    
    # Attribute primaryScript uses Python identifier primaryScript
    __primaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryScript'), 'primaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_primaryScript', _module_typeBindings.ScriptSimpleType)
    __primaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 270, 3)
    __primaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 270, 3)
    
    primaryScript = property(__primaryScript.value, __primaryScript.set, None, '\n\t\t\t\t\t\tThe primary script used in the region\n\t\t\t\t\t')

    
    # Attribute secondaryScript uses Python identifier secondaryScript
    __secondaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'secondaryScript'), 'secondaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_secondaryScript', _module_typeBindings.ScriptSimpleType)
    __secondaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 278, 3)
    __secondaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 278, 3)
    
    secondaryScript = property(__secondaryScript.value, __secondaryScript.set, None, '\n\t\t\t\t\t\tThe secondary script used in the region\n\t\t\t\t\t')

    
    # Attribute production uses Python identifier production
    __production = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'production'), 'production', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextRegionType_production', _module_typeBindings.ProductionSimpleType)
    __production._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 286, 3)
    __production._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 286, 3)
    
    production = property(__production.value, __production.set, None, None)

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        __TextLine.name() : __TextLine,
        __TextEquiv.name() : __TextEquiv,
        __TextStyle.name() : __TextStyle
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __type.name() : __type,
        __leading.name() : __leading,
        __readingDirection.name() : __readingDirection,
        __textLineOrder.name() : __textLineOrder,
        __readingOrientation.name() : __readingOrientation,
        __indented.name() : __indented,
        __align.name() : __align,
        __primaryLanguage.name() : __primaryLanguage,
        __secondaryLanguage.name() : __secondaryLanguage,
        __primaryScript.name() : __primaryScript,
        __secondaryScript.name() : __secondaryScript,
        __production.name() : __production
    })
_module_typeBindings.TextRegionType = TextRegionType
Namespace.addCategoryObject('typeBinding', 'TextRegionType', TextRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}CoordsType with content type EMPTY
class CoordsType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}CoordsType with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CoordsType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 290, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute points uses Python identifier points
    __points = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'points'), 'points', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_CoordsType_points', _module_typeBindings.PointsType, required=True)
    __points._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 291, 2)
    __points._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 291, 2)
    
    points = property(__points.value, __points.set, None, 'Point list with format "x1,y1 x2,y2 ..."')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __points.name() : __points
    })
_module_typeBindings.CoordsType = CoordsType
Namespace.addCategoryObject('typeBinding', 'CoordsType', CoordsType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextLineType with content type ELEMENT_ONLY
class TextLineType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextLineType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextLineType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 297, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 299, 3), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Baseline uses Python identifier Baseline
    __Baseline = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Baseline'), 'Baseline', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Baseline', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 300, 3), )

    
    Baseline = property(__Baseline.value, __Baseline.set, None, '\n\t\t\t\t\t\tMultiple connected points that mark the baseline\n\t\t\t\t\t\tof the glyphs\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Word uses Python identifier Word
    __Word = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Word'), 'Word', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Word', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 309, 3), )

    
    Word = property(__Word.value, __Word.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv uses Python identifier TextEquiv
    __TextEquiv = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), 'TextEquiv', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextEquiv', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 312, 3), )

    
    TextEquiv = property(__TextEquiv.value, __TextEquiv.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextStyle uses Python identifier TextStyle
    __TextStyle = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), 'TextStyle', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextStyle', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 315, 3), )

    
    TextStyle = property(__TextStyle.value, __TextStyle.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 318, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 320, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 320, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute primaryLanguage uses Python identifier primaryLanguage
    __primaryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryLanguage'), 'primaryLanguage', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_primaryLanguage', _module_typeBindings.LanguageSimpleType)
    __primaryLanguage._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 321, 2)
    __primaryLanguage._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 321, 2)
    
    primaryLanguage = property(__primaryLanguage.value, __primaryLanguage.set, None, '\n\t\t\t\t\tOverrides primaryLanguage attribute of parent text\n\t\t\t\t\tregion\n\t\t\t\t')

    
    # Attribute primaryScript uses Python identifier primaryScript
    __primaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryScript'), 'primaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_primaryScript', _module_typeBindings.ScriptSimpleType)
    __primaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 330, 2)
    __primaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 330, 2)
    
    primaryScript = property(__primaryScript.value, __primaryScript.set, None, '\n\t\t\t\t\tThe primary script used in the text line\n\t\t\t\t')

    
    # Attribute secondaryScript uses Python identifier secondaryScript
    __secondaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'secondaryScript'), 'secondaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_secondaryScript', _module_typeBindings.ScriptSimpleType)
    __secondaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 338, 2)
    __secondaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 338, 2)
    
    secondaryScript = property(__secondaryScript.value, __secondaryScript.set, None, '\n\t\t\t\t\tThe secondary script used in the text line \n\t\t\t\t')

    
    # Attribute readingDirection uses Python identifier readingDirection
    __readingDirection = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'readingDirection'), 'readingDirection', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_readingDirection', _module_typeBindings.ReadingDirectionSimpleType)
    __readingDirection._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 346, 2)
    __readingDirection._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 346, 2)
    
    readingDirection = property(__readingDirection.value, __readingDirection.set, None, '\n\t\t\t\t\tThe direction in which text in a text line should be read\n\t\t\t\t')

    
    # Attribute production uses Python identifier production
    __production = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'production'), 'production', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_production', _module_typeBindings.ProductionSimpleType)
    __production._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 354, 2)
    __production._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 354, 2)
    
    production = property(__production.value, __production.set, None, '\n\t\t\t\t\tOverrides the production attribute of the parent\n\t\t\t\t\ttext region\n\t\t\t\t')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 362, 2)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 362, 2)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextLineType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 367, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 367, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __Coords.name() : __Coords,
        __Baseline.name() : __Baseline,
        __Word.name() : __Word,
        __TextEquiv.name() : __TextEquiv,
        __TextStyle.name() : __TextStyle,
        __UserDefined.name() : __UserDefined
    })
    _AttributeMap.update({
        __id.name() : __id,
        __primaryLanguage.name() : __primaryLanguage,
        __primaryScript.name() : __primaryScript,
        __secondaryScript.name() : __secondaryScript,
        __readingDirection.name() : __readingDirection,
        __production.name() : __production,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.TextLineType = TextLineType
Namespace.addCategoryObject('typeBinding', 'TextLineType', TextLineType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}WordType with content type ELEMENT_ONLY
class WordType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}WordType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'WordType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 369, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 371, 3), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Glyph uses Python identifier Glyph
    __Glyph = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Glyph'), 'Glyph', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Glyph', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 372, 3), )

    
    Glyph = property(__Glyph.value, __Glyph.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv uses Python identifier TextEquiv
    __TextEquiv = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), 'TextEquiv', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextEquiv', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 375, 3), )

    
    TextEquiv = property(__TextEquiv.value, __TextEquiv.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextStyle uses Python identifier TextStyle
    __TextStyle = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), 'TextStyle', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextStyle', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 378, 3), )

    
    TextStyle = property(__TextStyle.value, __TextStyle.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 381, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 383, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 383, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute language uses Python identifier language
    __language = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'language'), 'language', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_language', _module_typeBindings.LanguageSimpleType)
    __language._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 384, 2)
    __language._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 384, 2)
    
    language = property(__language.value, __language.set, None, '\n\t\t\t\t\tOverrides primaryLanguage attribute of parent line\n\t\t\t\t\tand/or text region\n\t\t\t\t')

    
    # Attribute primaryScript uses Python identifier primaryScript
    __primaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'primaryScript'), 'primaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_primaryScript', _module_typeBindings.ScriptSimpleType)
    __primaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 392, 2)
    __primaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 392, 2)
    
    primaryScript = property(__primaryScript.value, __primaryScript.set, None, '\n\t\t\t\t\tThe primary script used in the word\n\t\t\t\t')

    
    # Attribute secondaryScript uses Python identifier secondaryScript
    __secondaryScript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'secondaryScript'), 'secondaryScript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_secondaryScript', _module_typeBindings.ScriptSimpleType)
    __secondaryScript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 400, 2)
    __secondaryScript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 400, 2)
    
    secondaryScript = property(__secondaryScript.value, __secondaryScript.set, None, '\n\t\t\t\t\tThe secondary script used in the word \n\t\t\t\t')

    
    # Attribute readingDirection uses Python identifier readingDirection
    __readingDirection = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'readingDirection'), 'readingDirection', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_readingDirection', _module_typeBindings.ReadingDirectionSimpleType)
    __readingDirection._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 408, 2)
    __readingDirection._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 408, 2)
    
    readingDirection = property(__readingDirection.value, __readingDirection.set, None, '\n\t\t\t\t\tThe direction in which characters in a word should be read\n\t\t\t\t')

    
    # Attribute production uses Python identifier production
    __production = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'production'), 'production', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_production', _module_typeBindings.ProductionSimpleType)
    __production._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 416, 2)
    __production._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 416, 2)
    
    production = property(__production.value, __production.set, None, '\n\t\t\t\t\tOverrides the production attribute of the parent\n\t\t\t\t\ttext line and/or text region.\n\t\t\t\t')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 424, 2)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 424, 2)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_WordType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 429, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 429, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __Coords.name() : __Coords,
        __Glyph.name() : __Glyph,
        __TextEquiv.name() : __TextEquiv,
        __TextStyle.name() : __TextStyle,
        __UserDefined.name() : __UserDefined
    })
    _AttributeMap.update({
        __id.name() : __id,
        __language.name() : __language,
        __primaryScript.name() : __primaryScript,
        __secondaryScript.name() : __secondaryScript,
        __readingDirection.name() : __readingDirection,
        __production.name() : __production,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.WordType = WordType
Namespace.addCategoryObject('typeBinding', 'WordType', WordType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GlyphType with content type ELEMENT_ONLY
class GlyphType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GlyphType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GlyphType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 431, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 433, 3), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Graphemes uses Python identifier Graphemes
    __Graphemes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Graphemes'), 'Graphemes', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Graphemes', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 434, 3), )

    
    Graphemes = property(__Graphemes.value, __Graphemes.set, None, '\n\t\t\t\t\t\tContainer for graphemes, grapheme groups and\n\t\t\t\t\t\tnon-printing characters\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv uses Python identifier TextEquiv
    __TextEquiv = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), 'TextEquiv', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextEquiv', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 443, 3), )

    
    TextEquiv = property(__TextEquiv.value, __TextEquiv.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextStyle uses Python identifier TextStyle
    __TextStyle = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), 'TextStyle', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextStyle', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 446, 3), )

    
    TextStyle = property(__TextStyle.value, __TextStyle.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 449, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 451, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 451, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute ligature uses Python identifier ligature
    __ligature = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ligature'), 'ligature', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_ligature', pyxb.binding.datatypes.boolean)
    __ligature._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 452, 2)
    __ligature._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 452, 2)
    
    ligature = property(__ligature.value, __ligature.set, None, None)

    
    # Attribute symbol uses Python identifier symbol
    __symbol = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'symbol'), 'symbol', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_symbol', pyxb.binding.datatypes.boolean)
    __symbol._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 454, 2)
    __symbol._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 454, 2)
    
    symbol = property(__symbol.value, __symbol.set, None, None)

    
    # Attribute script uses Python identifier script
    __script = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'script'), 'script', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_script', _module_typeBindings.ScriptSimpleType)
    __script._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 456, 2)
    __script._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 456, 2)
    
    script = property(__script.value, __script.set, None, '\n\t\t\t\t\tThe script used for the glyph\n\t\t\t\t')

    
    # Attribute production uses Python identifier production
    __production = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'production'), 'production', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_production', _module_typeBindings.ProductionSimpleType)
    __production._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 464, 2)
    __production._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 464, 2)
    
    production = property(__production.value, __production.set, None, '\n\t\t\t\t\tOverrides the production attribute of the parent\n\t\t\t\t\tword / text line / text region.\n\t\t\t\t')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 472, 2)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 472, 2)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GlyphType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 477, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 477, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __Coords.name() : __Coords,
        __Graphemes.name() : __Graphemes,
        __TextEquiv.name() : __TextEquiv,
        __TextStyle.name() : __TextStyle,
        __UserDefined.name() : __UserDefined
    })
    _AttributeMap.update({
        __id.name() : __id,
        __ligature.name() : __ligature,
        __symbol.name() : __symbol,
        __script.name() : __script,
        __production.name() : __production,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.GlyphType = GlyphType
Namespace.addCategoryObject('typeBinding', 'GlyphType', GlyphType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquivType with content type ELEMENT_ONLY
class TextEquivType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquivType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextEquivType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 479, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}PlainText uses Python identifier PlainText
    __PlainText = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'PlainText'), 'PlainText', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15PlainText', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 481, 3), )

    
    PlainText = property(__PlainText.value, __PlainText.set, None, '\n\t\t\t\t\t\tText in a "simple" form (ASCII or extended ASCII\n\t\t\t\t\t\tas mostly used for typing). I.e. no use of\n\t\t\t\t\t\tspecial characters for ligatures (should be\n\t\t\t\t\t\tstored as two separate characters) etc.\n\t\t\t\t\t')

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Unicode uses Python identifier Unicode
    __Unicode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Unicode'), 'Unicode', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Unicode', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 491, 3), )

    
    Unicode = property(__Unicode.value, __Unicode.set, None, '\n\t\t\t\t\t\tCorrect encoding of the original, always using\n\t\t\t\t\t\tthe corresponding Unicode code point. I.e.\n\t\t\t\t\t\tligatures have to be represented as one\n\t\t\t\t\t\tcharacter etc.\n\t\t\t\t\t')

    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'index'), 'index', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_index', _module_typeBindings.STD_ANON)
    __index._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 502, 2)
    __index._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 502, 2)
    
    index = property(__index.value, __index.set, None, 'Used for sort order in case multiple TextEquivs are defined. The text content with the lowest index should be interpreted as the main text content.')

    
    # Attribute conf uses Python identifier conf
    __conf = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'conf'), 'conf', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_conf', _module_typeBindings.STD_ANON_)
    __conf._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 512, 2)
    __conf._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 512, 2)
    
    conf = property(__conf.value, __conf.set, None, 'OCR confidence value (between 0 and 1)')

    
    # Attribute dataType uses Python identifier dataType
    __dataType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'dataType'), 'dataType', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_dataType', _module_typeBindings.TextDataTypeSimpleType)
    __dataType._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 523, 2)
    __dataType._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 523, 2)
    
    dataType = property(__dataType.value, __dataType.set, None, 'Type of text content (is it free text or a number, for instance)\nThis is only a descriptive attribute, the text type is not checked during XML validation')

    
    # Attribute dataTypeDetails uses Python identifier dataTypeDetails
    __dataTypeDetails = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'dataTypeDetails'), 'dataTypeDetails', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_dataTypeDetails', pyxb.binding.datatypes.string)
    __dataTypeDetails._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 529, 2)
    __dataTypeDetails._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 529, 2)
    
    dataTypeDetails = property(__dataTypeDetails.value, __dataTypeDetails.set, None, 'Refinement for dataType attribute. Can be a regular expression, for instance.')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextEquivType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 545, 8)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 545, 8)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __PlainText.name() : __PlainText,
        __Unicode.name() : __Unicode
    })
    _AttributeMap.update({
        __index.name() : __index,
        __conf.name() : __conf,
        __dataType.name() : __dataType,
        __dataTypeDetails.name() : __dataTypeDetails,
        __comments.name() : __comments
    })
_module_typeBindings.TextEquivType = TextEquivType
Namespace.addCategoryObject('typeBinding', 'TextEquivType', TextEquivType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegionType with content type ELEMENT_ONLY
class ImageRegionType (RegionType):
    """
				An image is considered to be more intricate and complex
				than a graphic. These can be photos or drawings.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ImageRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 547, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ImageRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 556, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 556, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute colourDepth uses Python identifier colourDepth
    __colourDepth = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'colourDepth'), 'colourDepth', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ImageRegionType_colourDepth', _module_typeBindings.ColourDepthSimpleType)
    __colourDepth._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 563, 4)
    __colourDepth._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 563, 4)
    
    colourDepth = property(__colourDepth.value, __colourDepth.set, None, '\n\t\t\t\t\t\t\tThe colour bit depth required for the region\n\t\t\t\t\t\t')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ImageRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 571, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 571, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute embText uses Python identifier embText
    __embText = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'embText'), 'embText', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ImageRegionType_embText', pyxb.binding.datatypes.boolean)
    __embText._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 579, 4)
    __embText._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 579, 4)
    
    embText = property(__embText.value, __embText.set, None, '\n\t\t\t\t\t\t\tSpecifies whether the region also contains\n\t\t\t\t\t\t\ttext\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __colourDepth.name() : __colourDepth,
        __bgColour.name() : __bgColour,
        __embText.name() : __embText
    })
_module_typeBindings.ImageRegionType = ImageRegionType
Namespace.addCategoryObject('typeBinding', 'ImageRegionType', ImageRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegionType with content type ELEMENT_ONLY
class LineDrawingRegionType (RegionType):
    """
				A line drawing is a single colour illustration without
				solid areas.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 591, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LineDrawingRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 600, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 600, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute penColour uses Python identifier penColour
    __penColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'penColour'), 'penColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LineDrawingRegionType_penColour', _module_typeBindings.ColourSimpleType)
    __penColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 607, 4)
    __penColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 607, 4)
    
    penColour = property(__penColour.value, __penColour.set, None, '\n\t\t\t\t\t\t\tThe pen (foreground) colour of the region\n\t\t\t\t\t\t')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LineDrawingRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 615, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 615, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute embText uses Python identifier embText
    __embText = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'embText'), 'embText', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_LineDrawingRegionType_embText', pyxb.binding.datatypes.boolean)
    __embText._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 623, 4)
    __embText._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 623, 4)
    
    embText = property(__embText.value, __embText.set, None, '\n\t\t\t\t\t\t\tSpecifies whether the region also contains\n\t\t\t\t\t\t\ttext\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __penColour.name() : __penColour,
        __bgColour.name() : __bgColour,
        __embText.name() : __embText
    })
_module_typeBindings.LineDrawingRegionType = LineDrawingRegionType
Namespace.addCategoryObject('typeBinding', 'LineDrawingRegionType', LineDrawingRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegionType with content type ELEMENT_ONLY
class GraphicRegionType (RegionType):
    """
				Regions containing simple graphics, such as a company
				logo, should be marked as graphic regions.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GraphicRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 635, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphicRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 644, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 644, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphicRegionType_type', _module_typeBindings.GraphicsTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 651, 4)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 651, 4)
    
    type = property(__type.value, __type.set, None, '\n\t\t\t\t\t\t\tThe type of graphic in the region\n\t\t\t\t\t\t')

    
    # Attribute numColours uses Python identifier numColours
    __numColours = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'numColours'), 'numColours', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphicRegionType_numColours', pyxb.binding.datatypes.int)
    __numColours._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 659, 4)
    __numColours._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 659, 4)
    
    numColours = property(__numColours.value, __numColours.set, None, '\n\t\t\t\t\t\t\tAn approximation of the number of colours\n\t\t\t\t\t\t\tused in the region\n\t\t\t\t\t\t')

    
    # Attribute embText uses Python identifier embText
    __embText = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'embText'), 'embText', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphicRegionType_embText', pyxb.binding.datatypes.boolean)
    __embText._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 668, 4)
    __embText._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 668, 4)
    
    embText = property(__embText.value, __embText.set, None, '\n\t\t\t\t\t\t\tSpecifies whether the region also contains\n\t\t\t\t\t\t\ttext.\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __type.name() : __type,
        __numColours.name() : __numColours,
        __embText.name() : __embText
    })
_module_typeBindings.GraphicRegionType = GraphicRegionType
Namespace.addCategoryObject('typeBinding', 'GraphicRegionType', GraphicRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegionType with content type ELEMENT_ONLY
class TableRegionType (RegionType):
    """
				Tabular data in any form is represented with a table
				region. Rows and columns may or may not have separator
				lines; these lines are not separator regions.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TableRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 680, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 690, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 690, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute rows uses Python identifier rows
    __rows = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'rows'), 'rows', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_rows', pyxb.binding.datatypes.int)
    __rows._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 697, 4)
    __rows._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 697, 4)
    
    rows = property(__rows.value, __rows.set, None, '\n\t\t\t\t\t\t\tThe number of rows present in the table\n\t\t\t\t\t\t')

    
    # Attribute columns uses Python identifier columns
    __columns = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'columns'), 'columns', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_columns', pyxb.binding.datatypes.int)
    __columns._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 704, 4)
    __columns._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 704, 4)
    
    columns = property(__columns.value, __columns.set, None, '\n\t\t\t\t\t\t\tThe number of columns present in the table\n\t\t\t\t\t\t')

    
    # Attribute lineColour uses Python identifier lineColour
    __lineColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'lineColour'), 'lineColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_lineColour', _module_typeBindings.ColourSimpleType)
    __lineColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 711, 4)
    __lineColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 711, 4)
    
    lineColour = property(__lineColour.value, __lineColour.set, None, '\n\t\t\t\t\t\t\tThe colour of the lines used in the region\n\t\t\t\t\t\t')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 719, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 719, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute lineSeparators uses Python identifier lineSeparators
    __lineSeparators = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'lineSeparators'), 'lineSeparators', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_lineSeparators', pyxb.binding.datatypes.boolean)
    __lineSeparators._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 727, 4)
    __lineSeparators._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 727, 4)
    
    lineSeparators = property(__lineSeparators.value, __lineSeparators.set, None, '\n\t\t\t\t\t\t\tSpecifies the presence of line separators\n\t\t\t\t\t\t')

    
    # Attribute embText uses Python identifier embText
    __embText = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'embText'), 'embText', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TableRegionType_embText', pyxb.binding.datatypes.boolean)
    __embText._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 735, 4)
    __embText._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 735, 4)
    
    embText = property(__embText.value, __embText.set, None, '\n\t\t\t\t\t\t\tSpecifies whether the region also contains\n\t\t\t\t\t\t\ttext\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __rows.name() : __rows,
        __columns.name() : __columns,
        __lineColour.name() : __lineColour,
        __bgColour.name() : __bgColour,
        __lineSeparators.name() : __lineSeparators,
        __embText.name() : __embText
    })
_module_typeBindings.TableRegionType = TableRegionType
Namespace.addCategoryObject('typeBinding', 'TableRegionType', TableRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegionType with content type ELEMENT_ONLY
class ChartRegionType (RegionType):
    """
				Regions containing charts or graphs of any type, should
				be marked as chart regions.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ChartRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 747, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChartRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 756, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 756, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChartRegionType_type', _module_typeBindings.ChartTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 763, 4)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 763, 4)
    
    type = property(__type.value, __type.set, None, '\n\t\t\t\t\t\t\tThe type of chart in the region\n\t\t\t\t\t\t')

    
    # Attribute numColours uses Python identifier numColours
    __numColours = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'numColours'), 'numColours', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChartRegionType_numColours', pyxb.binding.datatypes.int)
    __numColours._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 771, 4)
    __numColours._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 771, 4)
    
    numColours = property(__numColours.value, __numColours.set, None, '\n\t\t\t\t\t\t\tAn approximation of the number of colours\n\t\t\t\t\t\t\tused in the region\n\t\t\t\t\t\t')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChartRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 780, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 780, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute embText uses Python identifier embText
    __embText = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'embText'), 'embText', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChartRegionType_embText', pyxb.binding.datatypes.boolean)
    __embText._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 788, 4)
    __embText._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 788, 4)
    
    embText = property(__embText.value, __embText.set, None, '\n\t\t\t\t\t\t\tSpecifies whether the region also contains\n\t\t\t\t\t\t\ttext\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __type.name() : __type,
        __numColours.name() : __numColours,
        __bgColour.name() : __bgColour,
        __embText.name() : __embText
    })
_module_typeBindings.ChartRegionType = ChartRegionType
Namespace.addCategoryObject('typeBinding', 'ChartRegionType', ChartRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegionType with content type ELEMENT_ONLY
class SeparatorRegionType (RegionType):
    """
				Separators are lines that lie between columns and
				paragraphs and can be used to logically separate
				different articles from each other.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 800, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_SeparatorRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 810, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 810, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute colour uses Python identifier colour
    __colour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'colour'), 'colour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_SeparatorRegionType_colour', _module_typeBindings.ColourSimpleType)
    __colour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 817, 4)
    __colour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 817, 4)
    
    colour = property(__colour.value, __colour.set, None, '\n\t\t\t\t\t\t\tThe colour of the separator\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __colour.name() : __colour
    })
_module_typeBindings.SeparatorRegionType = SeparatorRegionType
Namespace.addCategoryObject('typeBinding', 'SeparatorRegionType', SeparatorRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegionType with content type ELEMENT_ONLY
class MathsRegionType (RegionType):
    """
				Regions containing equations and mathematical symbols
				should be marked as maths regions.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'MathsRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 828, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MathsRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 837, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 837, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MathsRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 844, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 844, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __bgColour.name() : __bgColour
    })
_module_typeBindings.MathsRegionType = MathsRegionType
Namespace.addCategoryObject('typeBinding', 'MathsRegionType', MathsRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegionType with content type ELEMENT_ONLY
class ChemRegionType (RegionType):
    """
				Regions containing chemical formulas.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ChemRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 855, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChemRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 863, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 863, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, '\n\t\t\t\t\t\t\tThe angle the rectangle encapsulating a\n\t\t\t\t\t\t\tregion has to be rotated in clockwise\n\t\t\t\t\t\t\tdirection in order to correct the present\n\t\t\t\t\t\t\tskew (negative values indicate\n\t\t\t\t\t\t\tanti-clockwise rotation). Range:\n\t\t\t\t\t\t\t-179.999,180\n\t\t\t\t\t\t')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_ChemRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 877, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 877, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __bgColour.name() : __bgColour
    })
_module_typeBindings.ChemRegionType = ChemRegionType
Namespace.addCategoryObject('typeBinding', 'ChemRegionType', ChemRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegionType with content type ELEMENT_ONLY
class MusicRegionType (RegionType):
    """
				Regions containing musical notations.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'MusicRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 889, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MusicRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 897, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 897, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_MusicRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 904, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 904, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __bgColour.name() : __bgColour
    })
_module_typeBindings.MusicRegionType = MusicRegionType
Namespace.addCategoryObject('typeBinding', 'MusicRegionType', MusicRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegionType with content type ELEMENT_ONLY
class AdvertRegionType (RegionType):
    """
				Regions containing advertisements.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AdvertRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 915, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'orientation'), 'orientation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_AdvertRegionType_orientation', pyxb.binding.datatypes.float)
    __orientation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 923, 4)
    __orientation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 923, 4)
    
    orientation = property(__orientation.value, __orientation.set, None, 'The angle the rectangle encapsulating a region has to be rotated in clockwise direction in order to correct the present skew (negative values indicate anti-clockwise rotation).\nRange: -179.999,180\n\t\t\t\t\t\t')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_AdvertRegionType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 931, 4)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 931, 4)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, '\n\t\t\t\t\t\t\tThe background colour of the region\n\t\t\t\t\t\t')

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __orientation.name() : __orientation,
        __bgColour.name() : __bgColour
    })
_module_typeBindings.AdvertRegionType = AdvertRegionType
Namespace.addCategoryObject('typeBinding', 'AdvertRegionType', AdvertRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegionType with content type ELEMENT_ONLY
class NoiseRegionType (RegionType):
    """
				Noise regions are regions where no real data lies, only
				false data created by artifacts on the document or
				scanner noise.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NoiseRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 942, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.NoiseRegionType = NoiseRegionType
Namespace.addCategoryObject('typeBinding', 'NoiseRegionType', NoiseRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegionType with content type ELEMENT_ONLY
class UnknownRegionType (RegionType):
    """
				To be used if the region type cannot be ascertained.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UnknownRegionType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 954, 1)
    _ElementMap = RegionType._ElementMap.copy()
    _AttributeMap = RegionType._AttributeMap.copy()
    # Base type is RegionType
    
    # Element Coords ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UserDefined ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element Roles ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Roles) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TextRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ImageRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ImageRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element LineDrawingRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}LineDrawingRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element GraphicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element TableRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TableRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChartRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChartRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element SeparatorRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}SeparatorRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MathsRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MathsRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element ChemRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}ChemRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element MusicRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}MusicRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element AdvertRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}AdvertRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element NoiseRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NoiseRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Element UnknownRegion ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnknownRegion) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    
    # Attribute continuation inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.UnknownRegionType = UnknownRegionType
Namespace.addCategoryObject('typeBinding', 'UnknownRegionType', UnknownRegionType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroupIndexedType with content type ELEMENT_ONLY
class OrderedGroupIndexedType (pyxb.binding.basis.complexTypeDefinition):
    """
				Indexed group containing ordered elements
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexedType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 998, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1005, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRefIndexed uses Python identifier RegionRefIndexed
    __RegionRefIndexed = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexed'), 'RegionRefIndexed', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15RegionRefIndexed', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1010, 4), )

    
    RegionRefIndexed = property(__RegionRefIndexed.value, __RegionRefIndexed.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroupIndexed uses Python identifier OrderedGroupIndexed
    __OrderedGroupIndexed = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexed'), 'OrderedGroupIndexed', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15OrderedGroupIndexed', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1013, 4), )

    
    OrderedGroupIndexed = property(__OrderedGroupIndexed.value, __OrderedGroupIndexed.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroupIndexed uses Python identifier UnorderedGroupIndexed
    __UnorderedGroupIndexed = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexed'), 'UnorderedGroupIndexed', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnorderedGroupIndexed', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1016, 4), )

    
    UnorderedGroupIndexed = property(__UnorderedGroupIndexed.value, __UnorderedGroupIndexed.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1021, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1021, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute regionRef uses Python identifier regionRef
    __regionRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'regionRef'), 'regionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_regionRef', pyxb.binding.datatypes.IDREF)
    __regionRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1022, 8)
    __regionRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1022, 8)
    
    regionRef = property(__regionRef.value, __regionRef.set, None, 'Optional link to a parent region of nested regions. The parent region doubles as reading order group. Only the nested regions should be allowed as group members.')

    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'index'), 'index', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_index', pyxb.binding.datatypes.int, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1025, 8)
    __index._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1025, 8)
    
    index = property(__index.value, __index.set, None, '\n\t\t\t\t\tPosition (order number) of this item within the\n\t\t\t\t\tcurrent hierarchy level.\n\t\t\t\t')

    
    # Attribute caption uses Python identifier caption
    __caption = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'caption'), 'caption', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_caption', pyxb.binding.datatypes.string)
    __caption._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1033, 2)
    __caption._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1033, 2)
    
    caption = property(__caption.value, __caption.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_type', _module_typeBindings.GroupTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1034, 2)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1034, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute continuation uses Python identifier continuation
    __continuation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'continuation'), 'continuation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_continuation', pyxb.binding.datatypes.boolean)
    __continuation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1035, 2)
    __continuation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1035, 2)
    
    continuation = property(__continuation.value, __continuation.set, None, '\n\t\t\t\t\tIs this group a continuation of another group (from\n\t\t\t\t\tprevious column or page, for example)?\n\t\t\t\t')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1043, 2)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1043, 2)
    
    custom = property(__custom.value, __custom.set, None, None)

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupIndexedType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1044, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1044, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __UserDefined.name() : __UserDefined,
        __RegionRefIndexed.name() : __RegionRefIndexed,
        __OrderedGroupIndexed.name() : __OrderedGroupIndexed,
        __UnorderedGroupIndexed.name() : __UnorderedGroupIndexed
    })
    _AttributeMap.update({
        __id.name() : __id,
        __regionRef.name() : __regionRef,
        __index.name() : __index,
        __caption.name() : __caption,
        __type.name() : __type,
        __continuation.name() : __continuation,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.OrderedGroupIndexedType = OrderedGroupIndexedType
Namespace.addCategoryObject('typeBinding', 'OrderedGroupIndexedType', OrderedGroupIndexedType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroupIndexedType with content type ELEMENT_ONLY
class UnorderedGroupIndexedType (pyxb.binding.basis.complexTypeDefinition):
    """
				Indexed group containing unordered elements
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexedType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1047, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1054, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRef uses Python identifier RegionRef
    __RegionRef = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), 'RegionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15RegionRef', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1058, 4), )

    
    RegionRef = property(__RegionRef.value, __RegionRef.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroup uses Python identifier OrderedGroup
    __OrderedGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup'), 'OrderedGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15OrderedGroup', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1059, 4), )

    
    OrderedGroup = property(__OrderedGroup.value, __OrderedGroup.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroup uses Python identifier UnorderedGroup
    __UnorderedGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup'), 'UnorderedGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnorderedGroup', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1062, 4), )

    
    UnorderedGroup = property(__UnorderedGroup.value, __UnorderedGroup.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1067, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1067, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute regionRef uses Python identifier regionRef
    __regionRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'regionRef'), 'regionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_regionRef', pyxb.binding.datatypes.IDREF)
    __regionRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1068, 8)
    __regionRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1068, 8)
    
    regionRef = property(__regionRef.value, __regionRef.set, None, 'Optional link to a parent region of nested regions. The parent region doubles as reading order group. Only the nested regions should be allowed as group members.')

    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'index'), 'index', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_index', pyxb.binding.datatypes.int, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1071, 2)
    __index._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1071, 2)
    
    index = property(__index.value, __index.set, None, '\n\t\t\t\t\tPosition (order number) of this item within the\n\t\t\t\t\tcurrent hierarchy level.\n\t\t\t\t')

    
    # Attribute caption uses Python identifier caption
    __caption = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'caption'), 'caption', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_caption', pyxb.binding.datatypes.string)
    __caption._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1079, 2)
    __caption._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1079, 2)
    
    caption = property(__caption.value, __caption.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_type', _module_typeBindings.GroupTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1080, 2)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1080, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute continuation uses Python identifier continuation
    __continuation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'continuation'), 'continuation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_continuation', pyxb.binding.datatypes.boolean)
    __continuation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1081, 8)
    __continuation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1081, 8)
    
    continuation = property(__continuation.value, __continuation.set, None, 'Is this group a continuation of another group (from previous column or page, for example)?')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1084, 8)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1084, 8)
    
    custom = property(__custom.value, __custom.set, None, None)

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupIndexedType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1085, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1085, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __UserDefined.name() : __UserDefined,
        __RegionRef.name() : __RegionRef,
        __OrderedGroup.name() : __OrderedGroup,
        __UnorderedGroup.name() : __UnorderedGroup
    })
    _AttributeMap.update({
        __id.name() : __id,
        __regionRef.name() : __regionRef,
        __index.name() : __index,
        __caption.name() : __caption,
        __type.name() : __type,
        __continuation.name() : __continuation,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.UnorderedGroupIndexedType = UnorderedGroupIndexedType
Namespace.addCategoryObject('typeBinding', 'UnorderedGroupIndexedType', UnorderedGroupIndexedType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroupType with content type ELEMENT_ONLY
class OrderedGroupType (pyxb.binding.basis.complexTypeDefinition):
    """
				Numbered group (contains ordered elements)
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1092, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1099, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRefIndexed uses Python identifier RegionRefIndexed
    __RegionRefIndexed = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexed'), 'RegionRefIndexed', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15RegionRefIndexed', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1103, 4), )

    
    RegionRefIndexed = property(__RegionRefIndexed.value, __RegionRefIndexed.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroupIndexed uses Python identifier OrderedGroupIndexed
    __OrderedGroupIndexed = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexed'), 'OrderedGroupIndexed', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15OrderedGroupIndexed', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1106, 4), )

    
    OrderedGroupIndexed = property(__OrderedGroupIndexed.value, __OrderedGroupIndexed.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroupIndexed uses Python identifier UnorderedGroupIndexed
    __UnorderedGroupIndexed = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexed'), 'UnorderedGroupIndexed', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnorderedGroupIndexed', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1109, 4), )

    
    UnorderedGroupIndexed = property(__UnorderedGroupIndexed.value, __UnorderedGroupIndexed.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1114, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1114, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute regionRef uses Python identifier regionRef
    __regionRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'regionRef'), 'regionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_regionRef', pyxb.binding.datatypes.IDREF)
    __regionRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1115, 8)
    __regionRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1115, 8)
    
    regionRef = property(__regionRef.value, __regionRef.set, None, 'Optional link to a parent region of nested regions. The parent region doubles as reading order group. Only the nested regions should be allowed as group members.')

    
    # Attribute caption uses Python identifier caption
    __caption = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'caption'), 'caption', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_caption', pyxb.binding.datatypes.string)
    __caption._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1118, 2)
    __caption._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1118, 2)
    
    caption = property(__caption.value, __caption.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_type', _module_typeBindings.GroupTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1119, 2)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1119, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute continuation uses Python identifier continuation
    __continuation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'continuation'), 'continuation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_continuation', pyxb.binding.datatypes.boolean)
    __continuation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1120, 8)
    __continuation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1120, 8)
    
    continuation = property(__continuation.value, __continuation.set, None, 'Is this group a continuation of another group (from previous column or page, for example)?')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1124, 8)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1124, 8)
    
    custom = property(__custom.value, __custom.set, None, None)

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_OrderedGroupType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1125, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1125, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __UserDefined.name() : __UserDefined,
        __RegionRefIndexed.name() : __RegionRefIndexed,
        __OrderedGroupIndexed.name() : __OrderedGroupIndexed,
        __UnorderedGroupIndexed.name() : __UnorderedGroupIndexed
    })
    _AttributeMap.update({
        __id.name() : __id,
        __regionRef.name() : __regionRef,
        __caption.name() : __caption,
        __type.name() : __type,
        __continuation.name() : __continuation,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.OrderedGroupType = OrderedGroupType
Namespace.addCategoryObject('typeBinding', 'OrderedGroupType', OrderedGroupType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroupType with content type ELEMENT_ONLY
class UnorderedGroupType (pyxb.binding.basis.complexTypeDefinition):
    """
				Numbered group (contains unordered elements)
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1128, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserDefined uses Python identifier UserDefined
    __UserDefined = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), 'UserDefined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UserDefined', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1135, 3), )

    
    UserDefined = property(__UserDefined.value, __UserDefined.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRef uses Python identifier RegionRef
    __RegionRef = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), 'RegionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15RegionRef', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1139, 4), )

    
    RegionRef = property(__RegionRef.value, __RegionRef.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}OrderedGroup uses Python identifier OrderedGroup
    __OrderedGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup'), 'OrderedGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15OrderedGroup', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1140, 4), )

    
    OrderedGroup = property(__OrderedGroup.value, __OrderedGroup.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UnorderedGroup uses Python identifier UnorderedGroup
    __UnorderedGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup'), 'UnorderedGroup', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15UnorderedGroup', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1143, 4), )

    
    UnorderedGroup = property(__UnorderedGroup.value, __UnorderedGroup.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1148, 2)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1148, 2)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute regionRef uses Python identifier regionRef
    __regionRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'regionRef'), 'regionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_regionRef', pyxb.binding.datatypes.IDREF)
    __regionRef._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1149, 8)
    __regionRef._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1149, 8)
    
    regionRef = property(__regionRef.value, __regionRef.set, None, 'Optional link to a parent region of nested regions. The parent region doubles as reading order group. Only the nested regions should be allowed as group members.')

    
    # Attribute caption uses Python identifier caption
    __caption = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'caption'), 'caption', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_caption', pyxb.binding.datatypes.string)
    __caption._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1152, 2)
    __caption._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1152, 2)
    
    caption = property(__caption.value, __caption.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_type', _module_typeBindings.GroupTypeSimpleType)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1153, 2)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1153, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute continuation uses Python identifier continuation
    __continuation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'continuation'), 'continuation', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_continuation', pyxb.binding.datatypes.boolean)
    __continuation._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1154, 8)
    __continuation._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1154, 8)
    
    continuation = property(__continuation.value, __continuation.set, None, 'Is this group a continuation of another group (from previous column or page, for example)?')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1157, 8)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1157, 8)
    
    custom = property(__custom.value, __custom.set, None, None)

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UnorderedGroupType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1158, 2)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1158, 2)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __UserDefined.name() : __UserDefined,
        __RegionRef.name() : __RegionRef,
        __OrderedGroup.name() : __OrderedGroup,
        __UnorderedGroup.name() : __UnorderedGroup
    })
    _AttributeMap.update({
        __id.name() : __id,
        __regionRef.name() : __regionRef,
        __caption.name() : __caption,
        __type.name() : __type,
        __continuation.name() : __continuation,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.UnorderedGroupType = UnorderedGroupType
Namespace.addCategoryObject('typeBinding', 'UnorderedGroupType', UnorderedGroupType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}BaselineType with content type EMPTY
class BaselineType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}BaselineType with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BaselineType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1679, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute points uses Python identifier points
    __points = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'points'), 'points', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_BaselineType_points', _module_typeBindings.PointsType, required=True)
    __points._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1680, 5)
    __points._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1680, 5)
    
    points = property(__points.value, __points.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __points.name() : __points
    })
_module_typeBindings.BaselineType = BaselineType
Namespace.addCategoryObject('typeBinding', 'BaselineType', BaselineType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RelationType with content type ELEMENT_ONLY
class RelationType (pyxb.binding.basis.complexTypeDefinition):
    """
    			One-to-one relation between to layout object. Use 'link'
    			for loose relations and 'join' for strong relations
    			(where something is fragmented for instance).

    			Examples for 'link': caption - image floating -
    			paragraph paragraph - paragraph (when a pragraph is
    			split across columns and the last word of the first
    			paragraph DOES NOT continue in the second paragraph)
    			drop-cap - paragraph (when the drop-cap is a whole word)

    			Examples for 'join': word - word (separated word at the
    			end of a line) drop-cap - paragraph (when the drop-cap
    			is not a whole word) paragraph - paragraph (when a
    			pragraph is split across columns and the last word of
    			the first paragraph DOES continue in the second
    			paragraph)
    		"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RelationType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1706, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}RegionRef uses Python identifier RegionRef
    __RegionRef = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), 'RegionRef', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RelationType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15RegionRef', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1728, 6), )

    
    RegionRef = property(__RegionRef.value, __RegionRef.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RelationType_type', _module_typeBindings.STD_ANON_2, required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1730, 5)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1730, 5)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RelationType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1738, 8)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1738, 8)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_RelationType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1741, 8)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1741, 8)
    
    comments = property(__comments.value, __comments.set, None, None)

    _ElementMap.update({
        __RegionRef.name() : __RegionRef
    })
    _AttributeMap.update({
        __type.name() : __type,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.RelationType = RelationType
Namespace.addCategoryObject('typeBinding', 'RelationType', RelationType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextStyleType with content type EMPTY
class TextStyleType (pyxb.binding.basis.complexTypeDefinition):
    """
    			Monospace (fixed-pitch, non-proportional) or
    			proportional font
    		"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextStyleType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1758, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute fontFamily uses Python identifier fontFamily
    __fontFamily = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'fontFamily'), 'fontFamily', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_fontFamily', pyxb.binding.datatypes.string)
    __fontFamily._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1765, 5)
    __fontFamily._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1765, 5)
    
    fontFamily = property(__fontFamily.value, __fontFamily.set, None, '\n    \t\t\t\tFor instance: Arial, Times New Roman. Add more\n    \t\t\t\tinformation if necessary (e.g. blackletter,\n    \t\t\t\tantiqua).\n    \t\t\t')

    
    # Attribute serif uses Python identifier serif
    __serif = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'serif'), 'serif', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_serif', pyxb.binding.datatypes.boolean)
    __serif._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1774, 5)
    __serif._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1774, 5)
    
    serif = property(__serif.value, __serif.set, None, '\n    \t\t\t\tSerif or sans-serif typeface\n    \t\t\t')

    
    # Attribute monospace uses Python identifier monospace
    __monospace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'monospace'), 'monospace', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_monospace', pyxb.binding.datatypes.boolean)
    __monospace._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1781, 5)
    __monospace._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1781, 5)
    
    monospace = property(__monospace.value, __monospace.set, None, None)

    
    # Attribute fontSize uses Python identifier fontSize
    __fontSize = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'fontSize'), 'fontSize', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_fontSize', pyxb.binding.datatypes.float)
    __fontSize._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1782, 5)
    __fontSize._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1782, 5)
    
    fontSize = property(__fontSize.value, __fontSize.set, None, '\n    \t\t\t\tThe size of the characters in points\n    \t\t\t')

    
    # Attribute xHeight uses Python identifier xHeight
    __xHeight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'xHeight'), 'xHeight', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_xHeight', pyxb.binding.datatypes.integer)
    __xHeight._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1789, 5)
    __xHeight._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1789, 5)
    
    xHeight = property(__xHeight.value, __xHeight.set, None, 'The x-height or corpus size refers to the distance between the baseline and the mean line of lower-case letters in a typeface. The unit is assumed to be pixels.')

    
    # Attribute kerning uses Python identifier kerning
    __kerning = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'kerning'), 'kerning', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_kerning', pyxb.binding.datatypes.int)
    __kerning._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1794, 5)
    __kerning._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1794, 5)
    
    kerning = property(__kerning.value, __kerning.set, None, '\n    \t\t\t\tThe degree of space (in points) between the\n    \t\t\t\tcharacters in a string of text\n    \t\t\t')

    
    # Attribute textColour uses Python identifier textColour
    __textColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'textColour'), 'textColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_textColour', _module_typeBindings.ColourSimpleType)
    __textColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1802, 5)
    __textColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1802, 5)
    
    textColour = property(__textColour.value, __textColour.set, None, None)

    
    # Attribute textColourRgb uses Python identifier textColourRgb
    __textColourRgb = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'textColourRgb'), 'textColourRgb', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_textColourRgb', pyxb.binding.datatypes.integer)
    __textColourRgb._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1803, 5)
    __textColourRgb._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1803, 5)
    
    textColourRgb = property(__textColourRgb.value, __textColourRgb.set, None, 'Text colour in RGB encoded format (red value) + (256 x green value) + (65536 x blue value)')

    
    # Attribute bgColour uses Python identifier bgColour
    __bgColour = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColour'), 'bgColour', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_bgColour', _module_typeBindings.ColourSimpleType)
    __bgColour._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1808, 5)
    __bgColour._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1808, 5)
    
    bgColour = property(__bgColour.value, __bgColour.set, None, 'Background colour')

    
    # Attribute bgColourRgb uses Python identifier bgColourRgb
    __bgColourRgb = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bgColourRgb'), 'bgColourRgb', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_bgColourRgb', pyxb.binding.datatypes.integer)
    __bgColourRgb._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1813, 5)
    __bgColourRgb._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1813, 5)
    
    bgColourRgb = property(__bgColourRgb.value, __bgColourRgb.set, None, 'Background colour in RGB encoded format (red value) + (256 x green value) + (65536 x blue value)')

    
    # Attribute reverseVideo uses Python identifier reverseVideo
    __reverseVideo = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'reverseVideo'), 'reverseVideo', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_reverseVideo', pyxb.binding.datatypes.boolean)
    __reverseVideo._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1818, 5)
    __reverseVideo._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1818, 5)
    
    reverseVideo = property(__reverseVideo.value, __reverseVideo.set, None, '\n    \t\t\t\tSpecifies whether the colour of the text appears\n    \t\t\t\treversed against a background colour\n    \t\t\t')

    
    # Attribute bold uses Python identifier bold
    __bold = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'bold'), 'bold', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_bold', pyxb.binding.datatypes.boolean)
    __bold._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1826, 5)
    __bold._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1826, 5)
    
    bold = property(__bold.value, __bold.set, None, None)

    
    # Attribute italic uses Python identifier italic
    __italic = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'italic'), 'italic', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_italic', pyxb.binding.datatypes.boolean)
    __italic._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1827, 5)
    __italic._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1827, 5)
    
    italic = property(__italic.value, __italic.set, None, None)

    
    # Attribute underlined uses Python identifier underlined
    __underlined = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'underlined'), 'underlined', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_underlined', pyxb.binding.datatypes.boolean)
    __underlined._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1828, 5)
    __underlined._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1828, 5)
    
    underlined = property(__underlined.value, __underlined.set, None, None)

    
    # Attribute subscript uses Python identifier subscript
    __subscript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'subscript'), 'subscript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_subscript', pyxb.binding.datatypes.boolean)
    __subscript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1829, 5)
    __subscript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1829, 5)
    
    subscript = property(__subscript.value, __subscript.set, None, None)

    
    # Attribute superscript uses Python identifier superscript
    __superscript = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'superscript'), 'superscript', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_superscript', pyxb.binding.datatypes.boolean)
    __superscript._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1830, 5)
    __superscript._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1830, 5)
    
    superscript = property(__superscript.value, __superscript.set, None, None)

    
    # Attribute strikethrough uses Python identifier strikethrough
    __strikethrough = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'strikethrough'), 'strikethrough', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_strikethrough', pyxb.binding.datatypes.boolean)
    __strikethrough._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1831, 5)
    __strikethrough._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1831, 5)
    
    strikethrough = property(__strikethrough.value, __strikethrough.set, None, None)

    
    # Attribute smallCaps uses Python identifier smallCaps
    __smallCaps = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'smallCaps'), 'smallCaps', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_smallCaps', pyxb.binding.datatypes.boolean)
    __smallCaps._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1832, 8)
    __smallCaps._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1832, 8)
    
    smallCaps = property(__smallCaps.value, __smallCaps.set, None, None)

    
    # Attribute letterSpaced uses Python identifier letterSpaced
    __letterSpaced = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'letterSpaced'), 'letterSpaced', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_TextStyleType_letterSpaced', pyxb.binding.datatypes.boolean)
    __letterSpaced._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1833, 8)
    __letterSpaced._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1833, 8)
    
    letterSpaced = property(__letterSpaced.value, __letterSpaced.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __fontFamily.name() : __fontFamily,
        __serif.name() : __serif,
        __monospace.name() : __monospace,
        __fontSize.name() : __fontSize,
        __xHeight.name() : __xHeight,
        __kerning.name() : __kerning,
        __textColour.name() : __textColour,
        __textColourRgb.name() : __textColourRgb,
        __bgColour.name() : __bgColour,
        __bgColourRgb.name() : __bgColourRgb,
        __reverseVideo.name() : __reverseVideo,
        __bold.name() : __bold,
        __italic.name() : __italic,
        __underlined.name() : __underlined,
        __subscript.name() : __subscript,
        __superscript.name() : __superscript,
        __strikethrough.name() : __strikethrough,
        __smallCaps.name() : __smallCaps,
        __letterSpaced.name() : __letterSpaced
    })
_module_typeBindings.TextStyleType = TextStyleType
Namespace.addCategoryObject('typeBinding', 'TextStyleType', TextStyleType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType with content type ELEMENT_ONLY
class GraphemeBaseType (pyxb.binding.basis.complexTypeDefinition):
    """Base type for graphemes, grapheme groups and non-printing characters"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GraphemeBaseType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2007, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv uses Python identifier TextEquiv
    __TextEquiv = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), 'TextEquiv', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15TextEquiv', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6), )

    
    TextEquiv = property(__TextEquiv.value, __TextEquiv.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_id', pyxb.binding.datatypes.ID, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2016, 5)
    __id._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2016, 5)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'index'), 'index', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_index', _module_typeBindings.STD_ANON_3, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2017, 5)
    __index._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2017, 5)
    
    index = property(__index.value, __index.set, None, 'Order index of grapheme, group, or non-printing character within the parent container (graphemes or glyph or grapheme group)')

    
    # Attribute ligature uses Python identifier ligature
    __ligature = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ligature'), 'ligature', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_ligature', pyxb.binding.datatypes.boolean)
    __ligature._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2027, 5)
    __ligature._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2027, 5)
    
    ligature = property(__ligature.value, __ligature.set, None, None)

    
    # Attribute charType uses Python identifier charType
    __charType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'charType'), 'charType', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_charType', _module_typeBindings.STD_ANON_4)
    __charType._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2028, 5)
    __charType._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2028, 5)
    
    charType = property(__charType.value, __charType.set, None, 'Type of character represented by the grapheme/group/non-printing character element')

    
    # Attribute custom uses Python identifier custom
    __custom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'custom'), 'custom', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_custom', pyxb.binding.datatypes.string)
    __custom._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2039, 5)
    __custom._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2039, 5)
    
    custom = property(__custom.value, __custom.set, None, 'For generic use')

    
    # Attribute comments uses Python identifier comments
    __comments = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comments'), 'comments', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeBaseType_comments', pyxb.binding.datatypes.string)
    __comments._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2042, 5)
    __comments._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2042, 5)
    
    comments = property(__comments.value, __comments.set, None, 'For generic use')

    _ElementMap.update({
        __TextEquiv.name() : __TextEquiv
    })
    _AttributeMap.update({
        __id.name() : __id,
        __index.name() : __index,
        __ligature.name() : __ligature,
        __charType.name() : __charType,
        __custom.name() : __custom,
        __comments.name() : __comments
    })
_module_typeBindings.GraphemeBaseType = GraphemeBaseType
Namespace.addCategoryObject('typeBinding', 'GraphemeBaseType', GraphemeBaseType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}UserAttributeType with content type EMPTY
class UserAttributeType (pyxb.binding.basis.complexTypeDefinition):
    """Structured custom data defined by name, type and value."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UserAttributeType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2091, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UserAttributeType_name', pyxb.binding.datatypes.string)
    __name._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2095, 8)
    __name._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2095, 8)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute description uses Python identifier description
    __description = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'description'), 'description', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UserAttributeType_description', pyxb.binding.datatypes.string)
    __description._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2096, 8)
    __description._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2096, 8)
    
    description = property(__description.value, __description.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UserAttributeType_type', _module_typeBindings.STD_ANON_5)
    __type._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2097, 5)
    __type._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2097, 5)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute value uses Python identifier value_
    __value = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'value'), 'value_', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_UserAttributeType_value', pyxb.binding.datatypes.string)
    __value._DeclarationLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2107, 5)
    __value._UseLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2107, 5)
    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __name.name() : __name,
        __description.name() : __description,
        __type.name() : __type,
        __value.name() : __value
    })
_module_typeBindings.UserAttributeType = UserAttributeType
Namespace.addCategoryObject('typeBinding', 'UserAttributeType', UserAttributeType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeType with content type ELEMENT_ONLY
class GraphemeType (GraphemeBaseType):
    """Represents a sub-element of a glyph. Smallest graphical unit that can be assigned a Unicode code point"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GraphemeType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2047, 4)
    _ElementMap = GraphemeBaseType._ElementMap.copy()
    _AttributeMap = GraphemeBaseType._AttributeMap.copy()
    # Base type is GraphemeBaseType
    
    # Element TextEquiv ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Coords uses Python identifier Coords
    __Coords = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Coords'), 'Coords', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Coords', False, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2054, 8), )

    
    Coords = property(__Coords.value, __Coords.set, None, None)

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute index inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute ligature inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute charType inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    _ElementMap.update({
        __Coords.name() : __Coords
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.GraphemeType = GraphemeType
Namespace.addCategoryObject('typeBinding', 'GraphemeType', GraphemeType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NonPrintingCharType with content type ELEMENT_ONLY
class NonPrintingCharType (GraphemeBaseType):
    """A glyph component without visual representation but with Unicode code point. Non-visual / non-printing / control character. Part of grapheme container (of glyph) or grapheme sub group."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NonPrintingCharType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2060, 4)
    _ElementMap = GraphemeBaseType._ElementMap.copy()
    _AttributeMap = GraphemeBaseType._AttributeMap.copy()
    # Base type is GraphemeBaseType
    
    # Element TextEquiv ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute index inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute ligature inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute charType inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.NonPrintingCharType = NonPrintingCharType
Namespace.addCategoryObject('typeBinding', 'NonPrintingCharType', NonPrintingCharType)


# Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeGroupType with content type ELEMENT_ONLY
class GraphemeGroupType (GraphemeBaseType):
    """Complex type {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeGroupType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GraphemeGroupType')
    _XSDLocation = pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2069, 4)
    _ElementMap = GraphemeBaseType._ElementMap.copy()
    _AttributeMap = GraphemeBaseType._AttributeMap.copy()
    # Base type is GraphemeBaseType
    
    # Element TextEquiv ({http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}TextEquiv) inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}Grapheme uses Python identifier Grapheme
    __Grapheme = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Grapheme'), 'Grapheme', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15Grapheme', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2073, 8), )

    
    Grapheme = property(__Grapheme.value, __Grapheme.set, None, None)

    
    # Element {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}NonPrintingChar uses Python identifier NonPrintingChar
    __NonPrintingChar = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'NonPrintingChar'), 'NonPrintingChar', '__httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15_GraphemeGroupType_httpschema_primaresearch_orgPAGEgtspagecontent2017_07_15NonPrintingChar', True, pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2074, 8), )

    
    NonPrintingChar = property(__NonPrintingChar.value, __NonPrintingChar.set, None, None)

    
    # Attribute id inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute index inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute ligature inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute charType inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute custom inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    
    # Attribute comments inherited from {http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15}GraphemeBaseType
    _ElementMap.update({
        __Grapheme.name() : __Grapheme,
        __NonPrintingChar.name() : __NonPrintingChar
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.GraphemeGroupType = GraphemeGroupType
Namespace.addCategoryObject('typeBinding', 'GraphemeGroupType', GraphemeGroupType)


PcGts = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PcGts'), PcGtsType, documentation='Page Content - Ground Truth and Storage', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 6, 4))
Namespace.addCategoryObject('elementBinding', PcGts.name().localName(), PcGts)



PcGtsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Metadata'), MetadataType, scope=PcGtsType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 12, 3)))

PcGtsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Page'), PageType, scope=PcGtsType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 13, 3)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PcGtsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Metadata')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 12, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PcGtsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Page')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 13, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PcGtsType._Automaton = _BuildAutomaton()




MetadataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Creator'), pyxb.binding.datatypes.string, scope=MetadataType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 19, 3)))

MetadataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Created'), pyxb.binding.datatypes.dateTime, scope=MetadataType, documentation='\n\t\t\t\t\t\tThe timestamp has to be in UTC (Coordinated\n\t\t\t\t\t\tUniversal Time) and not local time.\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 20, 3)))

MetadataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'LastChange'), pyxb.binding.datatypes.dateTime, scope=MetadataType, documentation='\n\t\t\t\t\t\tThe timestamp has to be in UTC (Coordinated\n\t\t\t\t\t\tUniversal Time) and not local time.\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 28, 3)))

MetadataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Comments'), pyxb.binding.datatypes.string, scope=MetadataType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 36, 3)))

MetadataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=MetadataType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 39, 3)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 36, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 39, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(MetadataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Creator')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 19, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(MetadataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Created')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 20, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(MetadataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LastChange')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 28, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(MetadataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Comments')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 36, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(MetadataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 39, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
MetadataType._Automaton = _BuildAutomaton_()




PrintSpaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=PrintSpaceType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 973, 3)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PrintSpaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 973, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PrintSpaceType._Automaton = _BuildAutomaton_2()




ReadingOrderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup'), OrderedGroupType, scope=ReadingOrderType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 982, 12)))

ReadingOrderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup'), UnorderedGroupType, scope=ReadingOrderType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 983, 12)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ReadingOrderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 982, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ReadingOrderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 983, 12))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ReadingOrderType._Automaton = _BuildAutomaton_3()




BorderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=BorderType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1166, 3)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BorderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1166, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BorderType._Automaton = _BuildAutomaton_4()




LayersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Layer'), LayerType, scope=LayersType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1664, 6)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(LayersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Layer')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1664, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
LayersType._Automaton = _BuildAutomaton_5()




LayerType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), RegionRefType, scope=LayerType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1671, 6)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(LayerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'RegionRef')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1671, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
LayerType._Automaton = _BuildAutomaton_6()




RelationsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Relation'), RelationType, scope=RelationsType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1702, 6)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RelationsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Relation')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1702, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
RelationsType._Automaton = _BuildAutomaton_7()




RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Roles'), RolesType, scope=RegionType, documentation='\n    \t\t\t\t\tRoles the region takes (e.g. in context of a\n    \t\t\t\t\tparent region)\n    \t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextRegion'), TextRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion'), ImageRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion'), LineDrawingRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion'), GraphicRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TableRegion'), TableRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion'), ChartRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion'), SeparatorRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion'), MathsRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion'), ChemRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion'), MusicRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion'), AdvertRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion'), NoiseRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7)))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion'), UnknownRegionType, scope=RegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
RegionType._Automaton = _BuildAutomaton_8()




GraphemesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Grapheme'), GraphemeType, scope=GraphemesType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2001, 6)))

GraphemesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'NonPrintingChar'), NonPrintingCharType, scope=GraphemesType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2002, 6)))

GraphemesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'GraphemeGroup'), GraphemeGroupType, scope=GraphemesType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2003, 6)))

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GraphemesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Grapheme')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2001, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GraphemesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NonPrintingChar')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2002, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GraphemesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphemeGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2003, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GraphemesType._Automaton = _BuildAutomaton_9()




UserDefinedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserAttribute'), UserAttributeType, scope=UserDefinedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2087, 6)))

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UserDefinedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserAttribute')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2087, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
UserDefinedType._Automaton = _BuildAutomaton_10()




RolesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TableCellRole'), TableCellRoleType, scope=RolesType, documentation='Data for a region that takes on the role of a table cell within a parent table region', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2131, 12)))

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2131, 12))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(RolesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableCellRole')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2131, 12))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
RolesType._Automaton = _BuildAutomaton_11()




PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AlternativeImage'), AlternativeImageType, scope=PageType, documentation='\n\t\t\t\t\t\tAlternative document page images (e.g.\n\t\t\t\t\t\tblack-and-white)\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 48, 3)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Border'), BorderType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 58, 3)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PrintSpace'), PrintSpaceType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 61, 3)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ReadingOrder'), ReadingOrderType, scope=PageType, documentation='', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 64, 3)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Layers'), LayersType, scope=PageType, documentation='\n\t\t\t\t\t\tUnassigned regions are considered to be in the\n\t\t\t\t\t\t(virtual) default layer which is to be treated\n\t\t\t\t\t\tas below any other layers.\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 70, 3)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Relations'), RelationsType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 80, 3)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 83, 12)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextRegion'), TextRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 85, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion'), ImageRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 86, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion'), LineDrawingRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 88, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion'), GraphicRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 91, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TableRegion'), TableRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 94, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion'), ChartRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 96, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion'), SeparatorRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 98, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion'), MathsRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 101, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion'), ChemRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 103, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion'), MusicRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 104, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion'), AdvertRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 105, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion'), NoiseRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 108, 4)))

PageType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion'), UnknownRegionType, scope=PageType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 110, 4)))

def _BuildAutomaton_12 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 48, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 58, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 61, 3))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 64, 3))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 70, 3))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 80, 3))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 83, 12))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 84, 12))
    counters.add(cc_7)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AlternativeImage')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 48, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Border')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 58, 3))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'PrintSpace')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 61, 3))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ReadingOrder')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 64, 3))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Layers')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 70, 3))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Relations')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 80, 3))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 83, 12))
    st_6 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 85, 4))
    st_7 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 86, 4))
    st_8 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 88, 4))
    st_9 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 91, 4))
    st_10 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 94, 4))
    st_11 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 96, 4))
    st_12 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 98, 4))
    st_13 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 101, 4))
    st_14 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 103, 4))
    st_15 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 104, 4))
    st_16 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 105, 4))
    st_17 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 108, 4))
    st_18 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_18)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(PageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 110, 4))
    st_19 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_19)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_17._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_18._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_19, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_19._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
PageType._Automaton = _BuildAutomaton_12()




TextRegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextLine'), TextLineType, scope=TextRegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 188, 4)))

TextRegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), TextEquivType, scope=TextRegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 191, 4)))

TextRegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), TextStyleType, scope=TextRegionType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 194, 4)))

def _BuildAutomaton_13 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_13
    del _BuildAutomaton_13
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 188, 4))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 191, 4))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 194, 4))
    counters.add(cc_5)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextLine')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 188, 4))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 191, 4))
    st_17 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(TextRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextStyle')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 194, 4))
    st_18 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_18)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    transitions.append(fac.Transition(st_16, [
         ]))
    transitions.append(fac.Transition(st_17, [
         ]))
    transitions.append(fac.Transition(st_18, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_17._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_18, [
        fac.UpdateInstruction(cc_5, True) ]))
    st_18._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TextRegionType._Automaton = _BuildAutomaton_13()




TextLineType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=TextLineType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 299, 3)))

TextLineType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Baseline'), BaselineType, scope=TextLineType, documentation='\n\t\t\t\t\t\tMultiple connected points that mark the baseline\n\t\t\t\t\t\tof the glyphs\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 300, 3)))

TextLineType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Word'), WordType, scope=TextLineType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 309, 3)))

TextLineType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), TextEquivType, scope=TextLineType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 312, 3)))

TextLineType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), TextStyleType, scope=TextLineType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 315, 3)))

TextLineType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=TextLineType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 318, 3)))

def _BuildAutomaton_14 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_14
    del _BuildAutomaton_14
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 300, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 309, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 312, 3))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 315, 3))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 318, 3))
    counters.add(cc_4)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TextLineType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 299, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(TextLineType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Baseline')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 300, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(TextLineType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Word')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 309, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TextLineType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 312, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(TextLineType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextStyle')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 315, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(TextLineType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 318, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, True) ]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TextLineType._Automaton = _BuildAutomaton_14()




WordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=WordType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 371, 3)))

WordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Glyph'), GlyphType, scope=WordType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 372, 3)))

WordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), TextEquivType, scope=WordType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 375, 3)))

WordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), TextStyleType, scope=WordType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 378, 3)))

WordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=WordType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 381, 3)))

def _BuildAutomaton_15 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_15
    del _BuildAutomaton_15
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 372, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 375, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 378, 3))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 381, 3))
    counters.add(cc_3)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(WordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 371, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(WordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Glyph')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 372, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(WordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 375, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(WordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextStyle')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 378, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(WordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 381, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
WordType._Automaton = _BuildAutomaton_15()




GlyphType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=GlyphType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 433, 3)))

GlyphType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Graphemes'), GraphemesType, scope=GlyphType, documentation='\n\t\t\t\t\t\tContainer for graphemes, grapheme groups and\n\t\t\t\t\t\tnon-printing characters\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 434, 3)))

GlyphType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), TextEquivType, scope=GlyphType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 443, 3)))

GlyphType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextStyle'), TextStyleType, scope=GlyphType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 446, 3)))

GlyphType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=GlyphType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 449, 3)))

def _BuildAutomaton_16 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_16
    del _BuildAutomaton_16
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 434, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 443, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 446, 3))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 449, 3))
    counters.add(cc_3)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GlyphType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 433, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(GlyphType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Graphemes')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 434, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(GlyphType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 443, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GlyphType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextStyle')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 446, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(GlyphType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 449, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GlyphType._Automaton = _BuildAutomaton_16()




TextEquivType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PlainText'), pyxb.binding.datatypes.string, scope=TextEquivType, documentation='\n\t\t\t\t\t\tText in a "simple" form (ASCII or extended ASCII\n\t\t\t\t\t\tas mostly used for typing). I.e. no use of\n\t\t\t\t\t\tspecial characters for ligatures (should be\n\t\t\t\t\t\tstored as two separate characters) etc.\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 481, 3)))

TextEquivType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Unicode'), pyxb.binding.datatypes.string, scope=TextEquivType, documentation='\n\t\t\t\t\t\tCorrect encoding of the original, always using\n\t\t\t\t\t\tthe corresponding Unicode code point. I.e.\n\t\t\t\t\t\tligatures have to be represented as one\n\t\t\t\t\t\tcharacter etc.\n\t\t\t\t\t', location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 491, 3)))

def _BuildAutomaton_17 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_17
    del _BuildAutomaton_17
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 481, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TextEquivType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'PlainText')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 481, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TextEquivType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Unicode')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 491, 3))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TextEquivType._Automaton = _BuildAutomaton_17()




def _BuildAutomaton_18 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_18
    del _BuildAutomaton_18
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ImageRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ImageRegionType._Automaton = _BuildAutomaton_18()




def _BuildAutomaton_19 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_19
    del _BuildAutomaton_19
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LineDrawingRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
LineDrawingRegionType._Automaton = _BuildAutomaton_19()




def _BuildAutomaton_20 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_20
    del _BuildAutomaton_20
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(GraphicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GraphicRegionType._Automaton = _BuildAutomaton_20()




def _BuildAutomaton_21 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_21
    del _BuildAutomaton_21
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TableRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TableRegionType._Automaton = _BuildAutomaton_21()




def _BuildAutomaton_22 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_22
    del _BuildAutomaton_22
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChartRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ChartRegionType._Automaton = _BuildAutomaton_22()




def _BuildAutomaton_23 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_23
    del _BuildAutomaton_23
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(SeparatorRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SeparatorRegionType._Automaton = _BuildAutomaton_23()




def _BuildAutomaton_24 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_24
    del _BuildAutomaton_24
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MathsRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
MathsRegionType._Automaton = _BuildAutomaton_24()




def _BuildAutomaton_25 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_25
    del _BuildAutomaton_25
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ChemRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ChemRegionType._Automaton = _BuildAutomaton_25()




def _BuildAutomaton_26 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_26
    del _BuildAutomaton_26
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(MusicRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
MusicRegionType._Automaton = _BuildAutomaton_26()




def _BuildAutomaton_27 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_27
    del _BuildAutomaton_27
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AdvertRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
AdvertRegionType._Automaton = _BuildAutomaton_27()




def _BuildAutomaton_28 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_28
    del _BuildAutomaton_28
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(NoiseRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
NoiseRegionType._Automaton = _BuildAutomaton_28()




def _BuildAutomaton_29 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_29
    del _BuildAutomaton_29
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1851, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1838, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1839, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Roles')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1842, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1852, 7))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImageRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1853, 7))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'LineDrawingRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1854, 7))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'GraphicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1857, 7))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TableRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1860, 7))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChartRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1861, 7))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SeparatorRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1862, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MathsRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1865, 7))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ChemRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1866, 7))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'MusicRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1867, 7))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AdvertRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1868, 7))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NoiseRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1871, 7))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(UnknownRegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnknownRegion')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1872, 7))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
UnknownRegionType._Automaton = _BuildAutomaton_29()




OrderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=OrderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1005, 3)))

OrderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexed'), RegionRefIndexedType, scope=OrderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1010, 4)))

OrderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexed'), OrderedGroupIndexedType, scope=OrderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1013, 4)))

OrderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexed'), UnorderedGroupIndexedType, scope=OrderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1016, 4)))

def _BuildAutomaton_30 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_30
    del _BuildAutomaton_30
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1005, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(OrderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1005, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(OrderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexed')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1010, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(OrderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexed')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1013, 4))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(OrderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexed')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1016, 4))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
OrderedGroupIndexedType._Automaton = _BuildAutomaton_30()




UnorderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=UnorderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1054, 3)))

UnorderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), RegionRefType, scope=UnorderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1058, 4)))

UnorderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup'), OrderedGroupType, scope=UnorderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1059, 4)))

UnorderedGroupIndexedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup'), UnorderedGroupType, scope=UnorderedGroupIndexedType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1062, 4)))

def _BuildAutomaton_31 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_31
    del _BuildAutomaton_31
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1054, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1054, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'RegionRef')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1058, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1059, 4))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupIndexedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1062, 4))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
UnorderedGroupIndexedType._Automaton = _BuildAutomaton_31()




OrderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=OrderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1099, 3)))

OrderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexed'), RegionRefIndexedType, scope=OrderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1103, 4)))

OrderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexed'), OrderedGroupIndexedType, scope=OrderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1106, 4)))

OrderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexed'), UnorderedGroupIndexedType, scope=OrderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1109, 4)))

def _BuildAutomaton_32 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_32
    del _BuildAutomaton_32
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1099, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(OrderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1099, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(OrderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'RegionRefIndexed')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1103, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(OrderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroupIndexed')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1106, 4))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(OrderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroupIndexed')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1109, 4))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
OrderedGroupType._Automaton = _BuildAutomaton_32()




UnorderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UserDefined'), UserDefinedType, scope=UnorderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1135, 3)))

UnorderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), RegionRefType, scope=UnorderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1139, 4)))

UnorderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup'), OrderedGroupType, scope=UnorderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1140, 4)))

UnorderedGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup'), UnorderedGroupType, scope=UnorderedGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1143, 4)))

def _BuildAutomaton_33 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_33
    del _BuildAutomaton_33
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1135, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UserDefined')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1135, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'RegionRef')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1139, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'OrderedGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1140, 4))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnorderedGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'UnorderedGroup')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1143, 4))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
UnorderedGroupType._Automaton = _BuildAutomaton_33()




RelationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionRef'), RegionRefType, scope=RelationType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1728, 6)))

def _BuildAutomaton_34 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_34
    del _BuildAutomaton_34
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=2, max=2, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1727, 5))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(RelationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'RegionRef')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 1728, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
RelationType._Automaton = _BuildAutomaton_34()




GraphemeBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv'), TextEquivType, scope=GraphemeBaseType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6)))

def _BuildAutomaton_35 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_35
    del _BuildAutomaton_35
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(GraphemeBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
GraphemeBaseType._Automaton = _BuildAutomaton_35()




GraphemeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Coords'), CoordsType, scope=GraphemeType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2054, 8)))

def _BuildAutomaton_36 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_36
    del _BuildAutomaton_36
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GraphemeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GraphemeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Coords')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2054, 8))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GraphemeType._Automaton = _BuildAutomaton_36()




def _BuildAutomaton_37 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_37
    del _BuildAutomaton_37
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(NonPrintingCharType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
NonPrintingCharType._Automaton = _BuildAutomaton_37()




GraphemeGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Grapheme'), GraphemeType, scope=GraphemeGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2073, 8)))

GraphemeGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'NonPrintingChar'), NonPrintingCharType, scope=GraphemeGroupType, location=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2074, 8)))

def _BuildAutomaton_38 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_38
    del _BuildAutomaton_38
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2072, 7))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(GraphemeGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TextEquiv')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2012, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(GraphemeGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Grapheme')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2073, 8))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(GraphemeGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'NonPrintingChar')), pyxb.utils.utility.Location('http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd', 2074, 8))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
GraphemeGroupType._Automaton = _BuildAutomaton_38()

