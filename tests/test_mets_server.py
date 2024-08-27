import re
from typing import Iterable, Tuple
from pytest import fixture, raises
import pytest
from tests.base import assets

from itertools import repeat
from multiprocessing import Process, Pool, Pipe, set_start_method
try:
    # necessary for macos
    set_start_method("fork")
except RuntimeError:
    pass
from shutil import rmtree, copytree
from os import remove, stat as os_stat
from os.path import exists
from time import sleep
from pathlib import Path
import stat
from uuid import uuid4

from requests.exceptions import ConnectionError

from ocrd import Resolver, OcrdMetsServer, Workspace
from ocrd_utils import pushd_popd, MIMETYPE_PAGE

WORKSPACE_DIR = '/tmp/ocrd-mets-server'
TRANSPORTS = ['/tmp/ocrd-mets-server.sock', 'http://127.0.0.1:12345']

@fixture(scope='function', name='start_mets_server', params=TRANSPORTS)
def fixture_start_mets_server(request) -> Iterable[Tuple[str, Workspace]]:
    def _start_mets_server(*args, **kwargs):
        mets_server = OcrdMetsServer(*args, **kwargs)
        mets_server.startup()

    mets_server_url = request.param

    if mets_server_url == TRANSPORTS[0]:
        if exists(mets_server_url):
            remove(mets_server_url)

    if exists(WORKSPACE_DIR):
        rmtree(WORKSPACE_DIR, ignore_errors=True)

    copytree(assets.path_to('SBB0000F29300010000/data'), WORKSPACE_DIR)
    workspace = Workspace(Resolver(), WORKSPACE_DIR)
    p = Process(target=_start_mets_server, kwargs={'workspace': workspace, 'url': request.param})
    p.start()
    sleep(1)  # sleep to start up server
    yield mets_server_url, Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=mets_server_url)
    p.terminate()
    rmtree(WORKSPACE_DIR, ignore_errors=True)

def add_file_server(x):
    mets_server_url, i = x
    workspace_server = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=mets_server_url)
    workspace_server.add_file(
        local_filename=f'local_filename{i}',
        mimetype=MIMETYPE_PAGE,
        page_id=f'page{i}',
        file_grp='FOO',
        file_id=f'FOO_page{i}_foo{i}',
        # url=f'url{i}'
    )

def add_agent_server(x):
    mets_server_url, i = x
    workspace_server = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=mets_server_url)
    workspace_server.mets.add_agent(
        name=f'proc{i}',
        _type='baz',
        othertype='foo',
        role='foo',
        otherrole='bar',
        notes=[({'foo': 'bar'}, f'note{i}')]
    )

def test_mets_server_add_file(start_mets_server):
    NO_FILES = 500

    mets_server_url, workspace_server = start_mets_server

    # add NO_FILES files in parallel
    with Pool() as pool:
        pool.map(add_file_server, zip(repeat(mets_server_url), range(NO_FILES)))

    assert set(workspace_server.mets.file_groups) == set( [
        'OCR-D-IMG',
        'OCR-D-GT-PAGE',
        'OCR-D-GT-ALTO',
        'OCR-D-SEG-PAGE',
        'OCR-D-SEG-DOC',
        'OCR-D-OCR-ANY',
        'OCR-D-IMG-DESKEW',
        'OCR-D-SEG-LINE',
        'OCR-D-OCR-TESS',
        'OCR-D-SEG-CLASS',
        'OCR-D-COR-CIS',
        'OCR-D-IMG-BIN',
        'OCR-D-IMG-DEWARP',
        'OCR-D-IMG-DESPECK',
        'OCR-D-COR-ASV',
        'OCR-D-IMG-CROP',
        'OCR-D-SEG-REGION',
        'FOO'
    ])
    assert len(workspace_server.mets.find_all_files(fileGrp='FOO')) == NO_FILES

    # not yet synced
    workspace_file = Workspace(Resolver(), WORKSPACE_DIR)
    assert len(workspace_file.mets.find_all_files(fileGrp='FOO')) == 0

    # sync
    workspace_server.mets.save()
    workspace_file.reload_mets()

    assert len(workspace_file.mets.find_all_files(fileGrp='FOO')) == NO_FILES

def test_mets_server_add_agents(start_mets_server):
    NO_AGENTS = 30

    mets_server_url, workspace_server = start_mets_server

    no_agents_before = len(workspace_server.mets.agents)

    # add NO_AGENTS agents in parallel
    with Pool() as pool:
        pool.map(add_agent_server, zip(repeat(mets_server_url), list(range(NO_AGENTS))))

    assert len(workspace_server.mets.agents) == NO_AGENTS + no_agents_before
    # XXX not a tuple
    assert workspace_server.mets.agents[-1].notes[0][0] == {'{https://ocr-d.de}foo': 'bar'}

    workspace_file = Workspace(Resolver(), WORKSPACE_DIR)
    assert len(workspace_file.mets.agents) == no_agents_before

    # sync
    workspace_server.mets.save()
    workspace_file.reload_mets()

    assert len(workspace_file.mets.agents) == NO_AGENTS + no_agents_before

def test_mets_server_str(start_mets_server):
    mets_server_url, workspace_server = start_mets_server
    workspace_server = Workspace(Resolver(), WORKSPACE_DIR, mets_server_url=mets_server_url)
    f = next(workspace_server.find_files())
    assert str(f) == '<ClientSideOcrdFile fileGrp=OCR-D-IMG, ID=FILE_0001_IMAGE, mimetype=image/tiff, url=---, local_filename=OCR-D-IMG/FILE_0001_IMAGE.tif]/>'
    a = workspace_server.mets.agents[0]
    assert str(a) == '<ClientSideOcrdAgent [type=OTHER, othertype=SOFTWARE, role=CREATOR, otherrole=---, name=DFG-Koordinierungsprojekt zur Weiterentwicklung von Verfahren der Optical Character Recognition (OCR-D)]/>'
    assert str(workspace_server.mets) == '<ClientSideOcrdMets[url=%s]>' % ('http+unix://%2Ftmp%2Focrd-mets-server.sock' if mets_server_url == TRANSPORTS[0] else TRANSPORTS[1])

def test_mets_test_unimplemented(start_mets_server):
    _, workspace_server = start_mets_server
    with raises(NotImplementedError):
        workspace_server.mets.rename_file_group('OCR-D-IMG', 'FOO')

def test_mets_server_different_workspaces(start_mets_server):
    mets_server_url, workspace_server = start_mets_server
    with raises(ValueError, match="differs from local workspace"):
        workspace = Resolver().workspace_from_url(assets.url_of('SBB0000F29300010000/data/mets.xml'), mets_server_url=mets_server_url)

def test_mets_test_unique_identifier(start_mets_server):
    _, workspace_server = start_mets_server
    assert workspace_server.mets.unique_identifier == 'http://resolver.staatsbibliothek-berlin.de/SBB0000F29300010000'

def test_mets_server_socket_permissions(start_mets_server):
    mets_server_url, _ = start_mets_server
    if mets_server_url == TRANSPORTS[1]:
        assert True, 'No permissions to test for TCP server'
    else:
        socket_perm = os_stat(mets_server_url).st_mode
        assert socket_perm & stat.S_IRUSR
        assert socket_perm & stat.S_IWUSR
        assert socket_perm & stat.S_IRGRP
        assert socket_perm & stat.S_IWGRP
        assert socket_perm & stat.S_IROTH
        assert socket_perm & stat.S_IWOTH

def test_mets_server_socket_stop(start_mets_server):
    mets_server_url, workspace_server = start_mets_server
    if mets_server_url == TRANSPORTS[1]:
        assert True, 'No stop conditions to test for TCP server'
    else:
        assert Path(mets_server_url).exists()
        assert workspace_server.mets.workspace_path == WORKSPACE_DIR
        workspace_server.mets.stop()
        with raises(ConnectionError):
            workspace_server.mets.file_groups
        # make sure the socket file was deleted on shutdown
        assert not Path(mets_server_url).exists()

def test_find_all_files(start_mets_server : Tuple[str, Workspace]):
    _, workspace_server = start_mets_server
    mets = workspace_server.mets
    assert len(mets.find_all_files()) == 35, '35 files total'
    assert len(mets.find_all_files(fileGrp='OCR-D-IMG')) == 3, '3 files in "OCR-D-IMG"'
    # TODO https://github.com/OCR-D/core/issues/1185
    # assert len(mets.find_all_files(include_fileGrp='OCR-D-IMG')) == 3, '3 files in "OCR-D-IMG"'
    assert len(mets.find_all_files(fileGrp='//OCR-D-I.*')) == 13, '13 files in "//OCR-D-I.*"'
    # TODO https://github.com/OCR-D/core/issues/1185
    # assert len(mets.find_all_files(fileGrp='//OCR-D-I.*', exclude_fileGrp=['OCR-D-IMG'])) == 10, '10 files in "//OCR-D-I.*" sans OCR-D-IMG'
    assert len(mets.find_all_files(ID="FILE_0001_IMAGE")) == 1, '1 files with ID "FILE_0001_IMAGE"'
    assert len(mets.find_all_files(ID="//FILE_0005_.*")) == 1, '1 files with ID "//FILE_0005_.*"'
    assert len(mets.find_all_files(pageId='PHYS_0001')) == 17, '17 files for page "PHYS_0001"'
    assert len(mets.find_all_files(mimetype='image/tiff')) == 13, '13 image/tiff'
    assert len(mets.find_all_files(mimetype='//application/.*')) == 22, '22 application/.*'
    assert len(mets.find_all_files(mimetype=MIMETYPE_PAGE)) == 20, '20 ' + MIMETYPE_PAGE
    assert len(mets.find_all_files(local_filename='OCR-D-IMG/FILE_0005_IMAGE.tif')) == 1, '1 FILE xlink:href="OCR-D-IMG/FILE_0005_IMAGE.tif"'
    assert len(mets.find_all_files(url='https://github.com/OCR-D/assets/raw/master/data/SBB0000F29300010000/00000001_DESKEW.tif')) == 1, '1 URL xlink:href="https://github.com/OCR-D/assets/raw/master/data/SBB0000F29300010000/00000001_DESKEW.tif"'
    assert len(mets.find_all_files(pageId='PHYS_0001..PHYS_0005')) == 35, '35 files for page "PHYS_0001..PHYS_0005"'
    assert len(mets.find_all_files(pageId='//PHYS_000(1|2)')) == 34, '34 files in PHYS_001 and PHYS_0002'
    assert len(mets.find_all_files(pageId='//PHYS_0001,//PHYS_0005')) == 18, '18 files in PHYS_001 and PHYS_0005 (two regexes)'
    assert len(mets.find_all_files(pageId='//PHYS_0005,PHYS_0001..PHYS_0002')) == 35, '35 files in //PHYS_0005,PHYS_0001..PHYS_0002'
    assert len(mets.find_all_files(pageId='//PHYS_0005,PHYS_0001..PHYS_0002')) == 35, '35 files in //PHYS_0005,PHYS_0001..PHYS_0002'
    assert len(mets.find_all_files(pageId='1..10')) == 35, '35 files in @ORDER range 1..10'
    assert len(mets.find_all_files(pageId='1..5')) == 35, '35 files in @ORDER range 1..10'
    assert len(mets.find_all_files(pageId='PHYS_0001,PHYS_0002,PHYS_0005')) == 35, '35 in PHYS_0001,PHYS_0002,PHYS_0005'
    assert len(mets.find_all_files(pageId='PHYS_0001..PHYS_0002,PHYS_0005')) == 35, '35 in PHYS_0001,PHYS_0002,PHYS_0005'
    assert len(mets.find_all_files(pageId='page 1..page 2,5')) == 35, '35 in PHYS_0001,PHYS_0002,PHYS_0005'
    assert len(mets.find_all_files(pageId='PHYS_0005,1..2')) == 35, '35 in PHYS_0001,PHYS_0002,PHYS_0005'
    # TODO https://github.com/OCR-D/core/issues/1185
    # with pytest.raises(ValueError, match='differ in their non-numeric part'):
    #     len(mets.find_all_files(pageId='1..PHYS_0002'))
    # with pytest.raises(ValueError, match=re.compile(f'match(es)? none')):
    #     mets.find_all_files(pageId='PHYS_0006..PHYS_0029')
    # with pytest.raises(ValueError, match=re.compile(f'match(es)? none')):
    #     mets.find_all_files(pageId='PHYS_0001-NOTEXIST')
    # with pytest.raises(ValueError, match=re.compile(f'match(es)? none')):
    #     mets.find_all_files(pageId='1..5,PHYS_0006..PHYS_0029')
    # with pytest.raises(ValueError, match=re.compile(f'match(es)? none')):
    #     mets.find_all_files(pageId='//PHYS000.*')

def test_reload(start_mets_server : Tuple[str, Workspace]):
    _, workspace_server = start_mets_server
    workspace_server_copy = Workspace(Resolver(), workspace_server.directory)
    assert len(workspace_server.mets.find_all_files()) == 35, '35 files total'
    assert len(workspace_server_copy.mets.find_all_files()) == 35, '35 files total'

    workspace_server_copy.add_file('FOO', ID='foo', mimetype='foo/bar', local_filename='mets.xml', pageId='foo')
    assert len(workspace_server.mets.find_all_files()) == 35, '35 files total'
    assert len(workspace_server_copy.mets.find_all_files()) == 36, '36 files total'

    workspace_server_copy.save_mets()
    print(workspace_server.mets.reload())
    assert len(workspace_server.mets.find_all_files()) == 36, '36 files total'

