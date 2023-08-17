from pytest import fixture, raises
from tests.base import assets

from multiprocessing import Process, Pool
from shutil import rmtree, copytree
from os import remove
from os.path import exists
from time import sleep


from ocrd import Resolver, OcrdMetsServer, Workspace
from ocrd_utils import pushd_popd, MIMETYPE_PAGE

WORKSPACE_DIR = '/tmp/ocrd-mets-server'
SOCKET_PATH   = '/tmp/ocrd-mets-server.sock'

@fixture(scope='session')
def start_mets_server():
    def _start_mets_server(*args, **kwargs):
        mets_server = OcrdMetsServer(*args, **kwargs)
        mets_server.startup()

    if exists(SOCKET_PATH):
        remove(SOCKET_PATH)

    if exists(WORKSPACE_DIR):
        rmtree(WORKSPACE_DIR, ignore_errors=True)

    copytree(assets.path_to('kant_aufklaerung_1784/data'), WORKSPACE_DIR)
    workspace = Workspace(Resolver(), WORKSPACE_DIR)
    # p = multiprocessing.Process(target=_start_mets_server, kwargs={'host': 'localhost', 'port': 12345, 'workspace': workspace})
    p = Process(target=_start_mets_server, kwargs={'workspace': workspace, 'url': SOCKET_PATH})
    p.start()
    # sleep to start up server
    sleep(2)
    yield p
    p.terminate()
    rmtree(WORKSPACE_DIR, ignore_errors=True)

@fixture()
def workspace_socket():
    yield Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=SOCKET_PATH)

def add_file_socket(i):
    workspace_socket = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=SOCKET_PATH)
    workspace_socket.add_file(local_filename=f'foo{i}', mimetype=MIMETYPE_PAGE, page_id=f'page{1}', file_grp='FOO', file_id=f'FOO_page{i}_foo{i}')

def add_agent_socket(i):
    workspace_socket = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=SOCKET_PATH)
    workspace_socket.mets.add_agent(
        name=f'proc{i}',
        _type='baz',
        othertype='foo',
        role='foo',
        otherrole='bar',
        notes=[({'foo': 'bar'}, f'note{i}')]
    )

def test_mets_server_add_file(start_mets_server, workspace_socket):
    NO_FILES = 500

    # add NO_FILES files in parallel
    with Pool() as pool:
        pool.map(add_file_socket, list(range(NO_FILES)))

    assert set(workspace_socket.mets.file_groups) == set( ['OCR-D-IMG', 'OCR-D-GT-PAGE', 'OCR-D-GT-ALTO', 'FOO'])
    assert len(workspace_socket.mets.find_all_files(fileGrp='FOO')) == NO_FILES
    assert len(workspace_socket.mets.find_all_files(file_grp='FOO')) == NO_FILES

    # not yet synced
    workspace_file = Workspace(Resolver(), WORKSPACE_DIR)
    assert len(workspace_file.mets.find_all_files(fileGrp='FOO')) == 0

    # sync
    workspace_socket.mets.save()
    workspace_file.reload_mets()

    assert len(workspace_file.mets.find_all_files(fileGrp='FOO')) == NO_FILES

def test_mets_server_add_agents(start_mets_server, workspace_socket):
    NO_AGENTS = 30

    no_agents_before = len(workspace_socket.mets.agents)

    # add NO_AGENTS agents in parallel
    with Pool() as pool:
        pool.map(add_agent_socket, list(range(NO_AGENTS)))

    assert len(workspace_socket.mets.agents) == NO_AGENTS + no_agents_before
    # XXX not a tuple
    assert workspace_socket.mets.agents[-1].notes[0][0] == {'{https://ocr-d.de}foo': 'bar'}

    workspace_file = Workspace(Resolver(), WORKSPACE_DIR)
    assert len(workspace_file.mets.agents) == no_agents_before

    # sync
    workspace_socket.mets.save()
    workspace_file.reload_mets()

    assert len(workspace_file.mets.agents) == NO_AGENTS + no_agents_before

def test_mets_server_str(start_mets_server, workspace_socket):
    workspace_socket = Workspace(Resolver(), WORKSPACE_DIR, mets_server_url=SOCKET_PATH)
    f = next(workspace_socket.find_files())
    assert str(f) == '<OcrdFile fileGrp=OCR-D-IMG, ID=INPUT_0017, mimetype=image/tiff, url=---, local_filename=OCR-D-IMG/INPUT_0017.tif]/>'
    a = workspace_socket.mets.agents[0]
    assert str(a) == '<OcrdAgent [type=---, othertype=SOFTWARE, role=CREATOR, otherrole=---, name=DFG-Koordinierungsprojekt zur Weiterentwicklung von Verfahren der Optical Character Recognition (OCR-D)]/>'
    assert str(workspace_socket.mets) == '<ClientSideOcrdMets[url=http+unix://%2Ftmp%2Focrd-mets-server.sock]>'

def test_mets_test_unimplemented(start_mets_server, workspace_socket):
    with raises(NotImplementedError):
        workspace_socket.mets.rename_file_group('OCR-D-IMG', 'FOO')

def test_mets_test_unique_identifier(start_mets_server, workspace_socket):
    assert workspace_socket.mets.unique_identifier == 'http://kant_aufklaerung_1784'
