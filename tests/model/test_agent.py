# -*- coding: utf-8 -*-

from ocrd_models import (
    OcrdAgent
)
from tests.base import (
    main
)


def test_init_role_no_name():
    ag = OcrdAgent(role='FOO')
    assert ag.role == 'FOO'
    assert ag.name is None


def test_init_role_as_string():
    ag = OcrdAgent(role='FOO')
    expected = '<OcrdAgent [type=---, othertype=---, role=FOO, otherrole=---, name=---]/>'
    assert expected == str(ag)


def test_init_otherrole_and_othertype():
    ag = OcrdAgent(otherrole='BAR', othertype='x')
    assert ag.role == 'OTHER'
    assert ag.otherrole == 'BAR'
    assert ag.othertype == 'x'


def test_init_othertype():
    ag = OcrdAgent(othertype='foobar')
    assert ag.type == 'OTHER'


def test_set_name():
    ag = OcrdAgent(name='foobar')
    assert ag.name == 'foobar'
    ag.name = 'barfoo' 
    assert ag.name == 'barfoo'


if __name__ == '__main__':
    main(__file__)
