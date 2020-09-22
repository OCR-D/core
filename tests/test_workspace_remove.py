# -*- coding: utf-8 -*-

import os
import shutil

import lxml.etree as ET
from tests.base import main

import pytest

from ocrd.resolver import (
    Resolver
)

from ocrd.workspace import (
    Workspace
)


def test_workspace_init_missing_mets():
    """Raise Exception when missing mets-file in workspace"""

    with pytest.raises(Exception) as exc:
        Workspace(Resolver(), "foo/bar")

    assert "File does not exist" in str(exc.value)


@pytest.fixture(name="workspace_directory")
def fixture_workspace_directory(tmpdir):
    src_data_kant = './tests/assets/kant_aufklaerung_1784/data'
    target_data_kant = str(tmpdir.join('kant_aufklaerung_1784').join('data'))
    shutil.copytree(src_data_kant, target_data_kant)
    return str(target_data_kant)


def test_workspace_remove_group_not_found(workspace_directory):
    """Group identified by name not found raises exception"""

    resolver = Resolver()
    workspace = Workspace(resolver, workspace_directory)
    with pytest.raises(Exception) as exc:
        workspace.remove_file_group('FOO-BAR')

    assert "No such fileGrp" in str(exc)


def test_workspace_remove_single_group_recursive(workspace_directory):
    """Remove single group recursive by name succeeds"""

    # arrange
    resolver = Resolver()
    workspace = Workspace(resolver, workspace_directory)
    files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-ALTO')
    assert len(files) == 2

    # act
    workspace.remove_file_group('OCR-D-GT-ALTO', recursive=True)

    # assert
    files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-ALTO')
    assert len(files) == 0


def test_workspace_remove_groups_unforce(workspace_directory):
    """Remove groups by pattern recursive"""

    # arrange
    original_data = ET.parse(os.path.join(workspace_directory, 'mets.xml')).getroot()
    alto_groups = original_data.findall('.//{http://www.loc.gov/METS/}fileGrp[@USE="OCR-D-GT-ALTO"]')
    assert len(alto_groups) == 1
    altos = alto_groups[0].findall('.//{http://www.loc.gov/METS/}file')
    assert len(altos) == 2

    # act
    resolver = Resolver()
    workspace = Workspace(resolver, workspace_directory)
    workspace.remove_file_group('//OCR-D-GT.*', recursive=True)
    workspace.save_mets()

    # assert
    written_data = ET.parse(os.path.join(workspace_directory, 'mets.xml')).getroot()
    assert written_data is not None
    groups_new = written_data.findall('.//{http://www.loc.gov/METS/}fileGrp[@USE="OCR-D-GT-ALTO"]')
    assert not groups_new

if __name__ == '__main__':
    main(__file__)
