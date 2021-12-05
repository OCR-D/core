# -*- coding: utf-8 -*-

from ocrd_models import OcrdAgent


def test_init_role_no_name():
    ag = OcrdAgent(role='FOO')
    assert 'FOO' == ag.role
    assert None == ag.name


def test_init_role_as_string():
    ag = OcrdAgent(role='FOO')
    expected = '<OcrdAgent [type=---, othertype=---, role=FOO, otherrole=---, name=---]/>'
    assert expected == str(ag)


def test_init_otherrole_and_othertype():
    ag = OcrdAgent(otherrole='BAR', othertype='x')
    assert 'OTHER' == ag.role
    assert 'BAR' == ag.otherrole
    assert 'x' == ag.othertype


def test_init_othertype():
    ag = OcrdAgent(othertype='foobar')
    assert 'OTHER' == ag.type


def test_set_name():
    ag = OcrdAgent(name='foobar')
    assert 'foobar' == ag.name
    ag.name = 'barfoo'
    assert 'barfoo' == ag.name
