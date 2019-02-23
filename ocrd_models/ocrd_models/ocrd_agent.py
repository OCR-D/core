"""
API to ``mets:agent``
"""
#  import os
from .constants import NAMESPACES as NS, TAG_METS_AGENT, TAG_METS_NAME
from .ocrd_xml_base import ET

class OcrdAgent():
    """
    Represents a <mets:agent>
    """

    #  @staticmethod
    #  from_el(el):
    #      role = el_agent.get('ROLE')
    #      _type = el_agent.get('TYPE')
    #      otherrole = el_agent.get('OTHERROLE')
    #      name_parts = string.split(el.find('mets:name', NS).text, ' ', 2)
    #      #  name = name_parts[0]
    #      #  version = name_parts[1][1:]     # v0.0.1 => 0.0.1
    #      return OcrdAgent(el, name, role, _type, otherrole)

    def __init__(self, el=None, name=None, _type=None, othertype=None, role=None, otherrole=None):
        """
        Args:
            el (LxmlElement):
            name (string):
            _type (string):
            othertype (string):
            role (string):
            otherrole (string):
        """
        if el is None:
            el = ET.Element(TAG_METS_AGENT)
        self._el = el
        self.name = name
        self.type = _type
        self.othertype = othertype
        self.role = role
        self.otherrole = otherrole

    def __str__(self):
        """
        String representation
        """
        props = ', '.join([
            '='.join([k, getattr(self, k) if getattr(self, k) else '---'])
            for k in ['type', 'othertype', 'role', 'otherrole', 'name']
        ])
        return '<OcrdAgent [' + props + ']/>'

    @property
    def type(self):
        """
        Get the ``TYPE`` attribute value.
        """
        return self._el.get('TYPE')

    @type.setter
    def type(self, _type):
        """
        Set the ``TYPE`` attribute value.
        """
        if _type is not None:
            self._el.set('TYPE', _type)

    @property
    def othertype(self):
        """
        Get the ``OTHERTYPE`` attribute value.
        """
        return self._el.get('OTHERTYPE')

    @othertype.setter
    def othertype(self, othertype):
        """
        Set the ``OTHERTYPE`` attribute value.
        """
        if othertype is not None:
            self._el.set('TYPE', 'OTHER')
            self._el.set('OTHERTYPE', othertype)

    @property
    def role(self):
        """
        Get the ``ROLE`` attribute value.
        """
        return self._el.get('ROLE')

    @role.setter
    def role(self, role):
        """
        Set the ``ROLE`` attribute value.
        """
        if role is not None:
            self._el.set('ROLE', role)

    @property
    def otherrole(self):
        """
        Get the ``OTHERROLE`` attribute value.
        """
        return self._el.get('OTHERROLE')

    @otherrole.setter
    def otherrole(self, otherrole):
        """
        Get the ``OTHERROLE`` attribute value.
        """
        if otherrole is not None:
            self._el.set('ROLE', 'OTHER')
            self._el.set('OTHERROLE', otherrole)

    @property
    def name(self):
        """
        Get the ``mets:name`` element value.
        """
        el_name = self._el.find('mets:name', NS)
        if el_name is not None:
            return el_name.text

    @name.setter
    def name(self, name):
        """
        Get the ``mets:name`` element value.
        """
        if name is not None:
            el_name = self._el.find('mets:name', NS)
            if el_name is None:
                el_name = ET.SubElement(self._el, TAG_METS_NAME)
            el_name.text = name
