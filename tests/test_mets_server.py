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
    p = Process(target=_start_mets_server, kwargs={'workspace': workspace, 'socket': SOCKET_PATH, 'host': None, 'port': None})
    p.start()
    # sleep to start up server
    sleep(2)
    yield p
    p.terminate()
    rmtree(WORKSPACE_DIR, ignore_errors=True)

def test_mets_server_invalid_args():
    with raises(ValueError):
        OcrdMetsServer(workspace=None, socket=True, host=True, port=True)
    with raises(ValueError):
        OcrdMetsServer(workspace=None, socket=False, host=False, port=True)
    with raises(ValueError):
        OcrdMetsServer(workspace=None, socket=False, host=True, port=False)

def add_file_socket(i):
    workspace_socket = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_socket=SOCKET_PATH)
    workspace_socket.add_file(url=f'foo{i}', mimetype=MIMETYPE_PAGE, page_id=f'page{1}', file_grp='FOO', file_id=f'FOO_page{i}_foo{i}')

def add_agent_socket(i):
    workspace_socket = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_socket=SOCKET_PATH)
    workspace_socket.mets.add_agent(
        name=f'proc{i}',
        _type='baz',
        othertype='foo',
        role='foo',
        otherrole='bar',
        notes=[({'foo': 'bar'}, f'note{i}')]
    )

def test_mets_server_add_file(start_mets_server):
    NO_FILES = 500

    # add NO_FILES files in parallel
    with Pool() as pool:
        pool.map(add_file_socket, list(range(NO_FILES)))

    workspace_socket = Workspace(Resolver(), WORKSPACE_DIR, mets_server_socket=SOCKET_PATH)

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

def test_mets_server_add_agents(start_mets_server):
    NO_AGENTS = 30

    workspace_socket = Workspace(Resolver(), WORKSPACE_DIR, mets_server_socket=SOCKET_PATH)
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
