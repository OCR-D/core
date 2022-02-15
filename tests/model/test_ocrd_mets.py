# -*- coding: utf-8 -*-

from datetime import datetime

from os.path import join
import shutil

from tests.base import (
    main,
    assets,
)

from ocrd_utils import (
    VERSION,
    MIMETYPE_PAGE
)
from ocrd_models import (
    OcrdMets
)

import pytest


@pytest.fixture(name='sbb_sample_01')
def _fixture():
    mets = OcrdMets(filename=assets.url_of(
        'SBB0000F29300010000/data/mets.xml'))
    yield mets


def test_unique_identifier():
    mets = OcrdMets(filename=assets.url_of('SBB0000F29300010000/data/mets.xml'))
    assert mets.unique_identifier == 'http://resolver.staatsbibliothek-berlin.de/SBB0000F29300010000', 'Right identifier'
    mets.unique_identifier = 'foo'
    assert mets.unique_identifier == 'foo', 'Right identifier after change'


def test_unique_identifier_from_nothing():
    mets = OcrdMets.empty_mets(datetime.now().isoformat())
    assert mets.unique_identifier == None, 'no identifier'
    mets.unique_identifier = 'foo'
    assert mets.unique_identifier == 'foo', 'Right identifier after change is "foo"'
    as_string = mets.to_xml().decode('utf-8')
    assert 'ocrd/core v%s' % VERSION in as_string
    assert 'CREATEDATE="%04u-%02u-%02uT' % (datetime.now().year, datetime.now().month, datetime.now().day,) in as_string


def test_str():
    mets = OcrdMets(content='<mets/>')
    assert str(mets) == 'OcrdMets[fileGrps=[],files=[]]'


@pytest.mark.xfail(reason='old test, was actually out-commented')
def test_override_constructor_args():
    id2file = {'foo': {}}
    mets = OcrdMets(id2file, content='<mets/>')
    assert mets._file_by_id == id2file


def test_file_groups(sbb_sample_01):
    assert len(sbb_sample_01.file_groups) == 17, '17 file groups shall be found'


def test_find_all_files(sbb_sample_01):
    assert len(sbb_sample_01.find_all_files()) == 35, '35 files total'
    assert len(sbb_sample_01.find_all_files(fileGrp='OCR-D-IMG')) == 3, '3 files in "OCR-D-IMG"'
    assert len(sbb_sample_01.find_all_files(fileGrp='//OCR-D-I.*')) == 13, '13 files in "//OCR-D-I.*"'
    assert len(sbb_sample_01.find_all_files(ID="FILE_0001_IMAGE")) == 1, '1 files with ID "FILE_0001_IMAGE"'
    assert len(sbb_sample_01.find_all_files(ID="//FILE_0005_.*")) == 1, '1 files with ID "//FILE_0005_.*"'
    assert len(sbb_sample_01.find_all_files(pageId='PHYS_0001')) == 17, '17 files for page "PHYS_0001"'
    assert len(sbb_sample_01.find_all_files(pageId='PHYS_0001-NOTEXIST')) == 0, '0 pages for "PHYS_0001-NOTEXIST"'
    assert len(sbb_sample_01.find_all_files(mimetype='image/tiff')) == 13, '13 image/tiff'
    assert len(sbb_sample_01.find_all_files(mimetype='//application/.*')) == 22, '22 application/.*'
    assert len(sbb_sample_01.find_all_files(mimetype=MIMETYPE_PAGE)) == 20, '20 ' + MIMETYPE_PAGE
    assert len(sbb_sample_01.find_all_files(url='OCR-D-IMG/FILE_0005_IMAGE.tif')) == 1, '1 xlink:href="OCR-D-IMG/FILE_0005_IMAGE.tif"'
    assert len(sbb_sample_01.find_all_files(pageId='PHYS_0001..PHYS_0005')) == 35, '35 files for page "PHYS_0001..PHYS_0005"'


def test_find_all_files_no_regex_for_pageid(sbb_sample_01):
    with pytest.raises(Exception) as exc_obj:
        sbb_sample_01.find_all_files(pageId='//foo')

    assert "not support regex search for pageId" in str(exc_obj.value)


def test_find_all_files_local_only(sbb_sample_01):
    assert len(sbb_sample_01.find_all_files(pageId='PHYS_0001',
               local_only=True)) == 3, '3 local files for page "PHYS_0001"'


def test_physical_pages(sbb_sample_01):
    assert len(sbb_sample_01.physical_pages) == 3, '3 physical pages'


def test_physical_pages_from_empty_mets():
    mets = OcrdMets(content="<mets></mets>")
    assert len(mets.physical_pages) == 0, 'no physical page'
    mets.add_file('OUTPUT', ID="foo123", pageId="foobar")
    assert len(mets.physical_pages) == 1, '1 physical page'


@pytest.fixture(name='sbb_directory_ocrd_mets')
def _fixture_sbb(tmp_path):
    src_path = assets.path_to('SBB0000F29300010000/data')
    dst_path = tmp_path / 'SBB_directory'
    shutil.copytree(src_path, dst_path)
    mets_path = str(join(dst_path, 'mets.xml'))
    yield OcrdMets(filename=mets_path)


def test_physical_pages_for_fileids(sbb_directory_ocrd_mets):
    assert sbb_directory_ocrd_mets.get_physical_pages(
        for_fileIds=['FILE_0002_IMAGE']) == ['PHYS_0002']


def test_add_group():
    mets = OcrdMets.empty_mets()
    assert len(mets.file_groups) == 0, '0 file groups'
    mets.add_file_group('TEST')
    assert len(mets.file_groups) == 1, '1 file groups'
    mets.add_file_group('TEST')
    assert len(mets.file_groups) == 1, '1 file groups'


def test_add_file():
    mets = OcrdMets.empty_mets()
    assert len(mets.file_groups) == 0, '0 file groups'
    assert len(list(mets.find_all_files(fileGrp='OUTPUT'))) == 0, '0 files in "OUTPUT"'
    f = mets.add_file('OUTPUT', ID="foo123", mimetype="bla/quux", pageId="foobar")
    f2 = mets.add_file('OUTPUT', ID="foo1232", mimetype="bla/quux", pageId="foobar")
    assert f.pageId == 'foobar', 'pageId set'
    assert len(mets.file_groups) == 1, '1 file groups'
    assert len(list(mets.find_all_files(fileGrp='OUTPUT'))) == 2, '2 files in "OUTPUT"'
    mets.set_physical_page_for_file('barfoo', f, order='300', orderlabel="page 300")
    assert f.pageId == 'barfoo', 'pageId changed'
    mets.set_physical_page_for_file('quux', f2, order='302', orderlabel="page 302")
    assert f2.pageId == 'quux', 'pageId changed'
    mets.set_physical_page_for_file('barfoo', f2, order='301', orderlabel="page 301")
    assert f2.pageId == 'barfoo', 'pageId changed'
    assert len(mets.file_groups) == 1, '1 file group'


def test_add_file_id_already_exists(sbb_sample_01):
    f = sbb_sample_01.add_file('OUTPUT', ID='best-id-ever', mimetype="beep/boop")
    assert f.ID == 'best-id-ever', "ID kept"
    with pytest.raises(Exception) as exc:
        sbb_sample_01.add_file('OUTPUT', ID='best-id-ever', mimetype="boop/beep")

    assert "File with ID='best-id-ever' already exists" in str(exc)

    f2 = sbb_sample_01.add_file('OUTPUT', ID='best-id-ever', mimetype="boop/beep", force=True)
    assert f._el == f2._el

@pytest.mark.xfail(reason='2x same ID is valid if ignore == True')
def test_add_file_ignore(sbb_sample_01: OcrdMets):
    """Behavior if ignore-Flag set to true:
    delegate responsibility to overwrite existing files to user"""

    the_file = sbb_sample_01.add_file('OUTPUT', ID='best-id-ever', mimetype="beep/boop")
    assert the_file.ID == 'best-id-ever'
    the_same = sbb_sample_01.add_file('OUTPUT', ID='best-id-ever', mimetype="boop/beep", ignore=True)
    assert the_same.ID == 'best-id-ever'

    # how many files inserted
    the_files = list(sbb_sample_01.find_files(ID='best-id-ever'))
    assert len(the_files) == 1


def test_add_file_id_invalid(sbb_sample_01):
    with pytest.raises(Exception) as exc:
        sbb_sample_01.add_file('OUTPUT', ID='1234:::', mimetype="beep/boop")
    assert "Invalid syntax for mets:file/@ID 1234:::" in str(exc)


def test_filegrp_from_file(sbb_sample_01):
    f = sbb_sample_01.find_all_files(fileGrp='OCR-D-IMG')[0]
    assert f.fileGrp == 'OCR-D-IMG'


def test_add_file_no_id(sbb_sample_01):
    with pytest.raises(Exception) as exc:
        sbb_sample_01.add_file('FOO')
    assert "Must set ID of the mets:file" in str(exc)


def test_add_file_no_pageid(sbb_sample_01):
    f = sbb_sample_01.add_file('OUTPUT', mimetype="bla/quux", ID="foo3")
    assert not f.pageId, 'No pageId available, dude!'


def test_file_pageid(sbb_sample_01):
    f = sbb_sample_01.find_all_files()[0]
    assert f.pageId == 'PHYS_0001'
    f.pageId = 'foo'
    assert f.pageId == 'foo'


def test_agent(sbb_sample_01):
    beforelen = len(sbb_sample_01.agents)
    sbb_sample_01.add_agent('foo bar v0.0.1', 'OTHER', 'OTHER', 'YETOTHERSTILL')
    assert len(sbb_sample_01.agents) == beforelen + 1


def test_metshdr():
    """
    Test whether metsHdr is created on-demand
    """
    mets = OcrdMets(content="<mets></mets>")
    assert not mets._tree.getroot().getchildren()
    mets.add_agent()
    assert len(mets._tree.getroot().getchildren()) == 1


def test_nocontent_nofilename_exception():
    with pytest.raises(Exception) as exc:
        OcrdMets()
    assert "Must pass 'filename' or 'content' to" in str(exc)


def test_encoding_entities():
    mets = OcrdMets(content="""
    <mets>
        <metsHdr>
        <agent>
            <name>Őh śéé Áŕ</name>
            <note>OCR-D</note>
        </agent>
        </metsHdr>
    </mets>
    """)
    assert 'Őh śéé Áŕ' in mets.to_xml().decode('utf-8')


def test_remove_page(sbb_directory_ocrd_mets):
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002', 'PHYS_0005']
    sbb_directory_ocrd_mets.remove_physical_page('PHYS_0001')
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0002', 'PHYS_0005']


def test_remove_physical_page_fptr(sbb_directory_ocrd_mets):
    assert sbb_directory_ocrd_mets.get_physical_pages(for_fileIds=['FILE_0002_IMAGE']), ['PHYS_0002']
    sbb_directory_ocrd_mets.remove_physical_page_fptr('FILE_0002_IMAGE')
    assert sbb_directory_ocrd_mets.get_physical_pages(for_fileIds=['FILE_0002_IMAGE']), [None]


def test_remove_page_after_remove_file(sbb_directory_ocrd_mets):
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002', 'PHYS_0005']
    sbb_directory_ocrd_mets.remove_one_file('FILE_0005_IMAGE')
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002']


def test_remove_file_ocrdfile(sbb_directory_ocrd_mets):
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002', 'PHYS_0005']
    ocrd_file = sbb_directory_ocrd_mets.find_all_files(ID='FILE_0005_IMAGE')[0]
    sbb_directory_ocrd_mets.remove_one_file(ocrd_file)
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002']


def test_remove_file_regex(sbb_directory_ocrd_mets):
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002', 'PHYS_0005']
    sbb_directory_ocrd_mets.remove_file('//FILE_0005.*')
    assert sbb_directory_ocrd_mets.physical_pages, ['PHYS_0001', 'PHYS_0002']


def test_rename_non_existent_filegroup_exception(sbb_directory_ocrd_mets):
    with pytest.raises(FileNotFoundError) as fnf_exc:
        sbb_directory_ocrd_mets.rename_file_group('FOOBAR', 'FOOBAR')
    # assert
    assert "No such fileGrp 'FOOBAR'" in str(fnf_exc)


def test_rename_file_group0(sbb_directory_ocrd_mets):
    assert 'FOOBAR' not in sbb_directory_ocrd_mets.file_groups

    # act
    sbb_directory_ocrd_mets.rename_file_group('OCR-D-GT-PAGE', 'FOOBAR')

    # assert
    assert 'OCR-D-GT-PAGE' not in sbb_directory_ocrd_mets.file_groups
    assert 'FOOBAR' in sbb_directory_ocrd_mets.file_groups


def test_remove_non_empty_filegroup_exception(sbb_directory_ocrd_mets):
    with pytest.raises(Exception) as exc:
        sbb_directory_ocrd_mets.remove_file_group('OCR-D-GT-ALTO')
    assert "not empty" in str(exc)


def test_remove_file_group0(sbb_directory_ocrd_mets):
    """
    Test removal of filegrp
    """

    assert len(sbb_directory_ocrd_mets.file_groups) == 17
    assert len(sbb_directory_ocrd_mets.find_all_files()) == 35

    sbb_directory_ocrd_mets.remove_file_group('OCR-D-GT-PAGE', recursive=True)
    assert len(sbb_directory_ocrd_mets.file_groups) == 16
    assert len(sbb_directory_ocrd_mets.find_all_files()) == 33


def test_remove_file_group_regex(sbb_directory_ocrd_mets):
    """
    Test removal of filegrp
    """

    assert len(sbb_directory_ocrd_mets.file_groups) == 17
    assert len(sbb_directory_ocrd_mets.find_all_files()) == 35

    # act
    sbb_directory_ocrd_mets.remove_file_group('//OCR-D-GT-.*', recursive=True)

    # assert
    assert len(sbb_directory_ocrd_mets.file_groups) == 15
    assert len(sbb_directory_ocrd_mets.find_all_files()) == 31


def test_merge(sbb_sample_01):
    assert len(sbb_sample_01.file_groups) == 17
    other_mets = OcrdMets(filename=assets.path_to('kant_aufklaerung_1784/data/mets.xml'))
    sbb_sample_01.merge(other_mets, fileGrp_mapping={'OCR-D-IMG': 'FOO'})
    assert len(sbb_sample_01.file_groups) == 18


def test_invalid_filegrp():
    """addresses https://github.com/OCR-D/core/issues/746"""

    mets = OcrdMets(content="<mets></mets>")
    with pytest.raises(ValueError) as val_err:
        mets.add_file('1:! bad filegrp', ID="foo123", pageId="foobar")

    assert "Invalid syntax for mets:fileGrp/@USE" in str(val_err.value)


if __name__ == '__main__':
    main(__file__)
