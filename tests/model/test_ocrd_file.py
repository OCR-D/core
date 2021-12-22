# -*- coding: utf-8 -*-

import pytest

from tests.base import (
    main,
    create_ocrd_file,
    create_ocrd_file_with_defaults
)
from ocrd_models import (
    OcrdMets,
    OcrdFile,
)


def test_ocrd_file_without_id():
    with pytest.raises(ValueError) as val_err:
        create_ocrd_file('FOO')

    assert "set ID" in str(val_err.value)


def test_ocrd_file_without_filegrp():
    with pytest.raises(ValueError) as val_err:
        create_ocrd_file(None, ID='foo')
    assert "set fileGrp" in str(val_err.value)


def test_set_loctype():
    f = create_ocrd_file_with_defaults()
    assert f.loctype == 'OTHER'
    assert f.otherloctype == 'FILE'
    f.otherloctype = 'foo'
    assert f.otherloctype == 'foo'
    f.loctype = 'URN'
    assert f.loctype == 'URN'
    assert f.otherloctype == None
    f.otherloctype = 'foo'
    assert f.loctype, 'OTHER'


def test_set_url():
    f = create_ocrd_file_with_defaults()
    f.url = None
    f.url = 'http://foo'
    f.url = 'http://bar'
    assert f.url == 'http://bar'


def test_constructor_url():
    f = create_ocrd_file_with_defaults(url="foo")
    assert f.url == 'foo'
    assert f.local_filename == 'foo'


def test_set_id_none():
    f = create_ocrd_file_with_defaults()
    f.ID = 'foo12'
    assert f.ID == 'foo12'
    f.ID = None
    assert f.ID == 'foo12'


def test_basename():
    f = create_ocrd_file_with_defaults(local_filename='/tmp/foo/bar/foo.bar')
    assert f.basename == 'foo.bar'


def test_basename_from_url():
    f = create_ocrd_file_with_defaults(url="http://foo.bar/quux")
    assert f.basename == 'quux'


@pytest.mark.parametrize("local_filename,extension",
                         [('/tmp/foo/bar/foo.bar', '.bar'),
                          ('/tmp/foo/bar/foo.tar.gz', '.tar.gz')]
                         )
def test_create_ocrd_file_with_defaults_extension(local_filename, extension):
    """Behavior for ocrd_file_with_defaults
    """

    f = create_ocrd_file_with_defaults(local_filename=local_filename)
    assert f.extension == extension


@pytest.mark.parametrize("local_filename,wo_extension",
                         [('/tmp/foo/bar/foo.bar', 'foo'),
                          ('/tmp/foo/bar/foo.tar.gz', 'foo')]
                         )
def test_create_ocrd_file_with_defaults_basename_wo_extension(local_filename, wo_extension):
    """Behavior for ocrd_file_with_defaults
    """

    f = create_ocrd_file_with_defaults(local_filename=local_filename)
    assert f.basename_without_extension == wo_extension


@pytest.mark.skip(reason="not possible anymore as of Fri Sep  3 13:11:00 CEST 2021")
def test_file_group_wo_parent():
    with pytest.raises(ValueError) as val_err:
        OcrdFile(None)
    assert "not related to METS" in str(val_err.value)


def test_file_group_wo_parent_new_version():
    """Test for new error message
    """
    with pytest.raises(ValueError, match=r"Must provide mets:file element this OcrdFile represent"):
        OcrdFile(None)

def test_ocrd_file_equality():
    mets = OcrdMets.empty_mets()
    f1 = mets.add_file('FOO', ID='FOO_1', mimetype='image/tiff')
    f2 = mets.add_file('FOO', ID='FOO_2', mimetype='image/tiff')
    assert f1 != f2
    f3 = create_ocrd_file_with_defaults(ID='TEMP_1', mimetype='image/tiff')
    f4 = create_ocrd_file_with_defaults(ID='TEMP_1', mimetype='image/tif')
    # be tolerant of different equivalent mimetypes
    assert f3 == f4
    f5 = mets.add_file('TEMP', ID='TEMP_1', mimetype='image/tiff')
    assert f3 == f5


def test_fptr_changed_for_change_id():
    mets = OcrdMets.empty_mets()
    f1 = mets.add_file('FOO', ID='FOO_1', mimetype='image/tiff', pageId='p0001')
    assert mets.get_physical_pages(for_fileIds=['FOO_1']) == ['p0001']
    f1.ID = 'BAZ_1'
    assert mets.get_physical_pages(for_fileIds=['FOO_1']) == [None]
    assert mets.get_physical_pages(for_fileIds=['BAZ_1']) == ['p0001']


if __name__ == '__main__':
    main(__file__)
