from pytest import fixture, raises
from tests.base import assets

from itertools import repeat
from multiprocessing import Process, Pool
from shutil import rmtree, copytree
from os import remove
from os.path import exists
from time import sleep


from ocrd import Resolver, OcrdMetsServer, Workspace
from ocrd_utils import pushd_popd, MIMETYPE_PAGE

WORKSPACE_DIR = '/tmp/ocrd-mets-server'
TRANSPORTS = ['/tmp/ocrd-mets-server.sock', 'http://localhost:12345']

@fixture(scope='session', name='start_mets_server', params=TRANSPORTS)
def fixture_start_mets_server(request):
    def _start_mets_server(*args, **kwargs):
        mets_server = OcrdMetsServer(*args, **kwargs)
        mets_server.startup()

    mets_server_url = request.param

    if mets_server_url == TRANSPORTS[0]:
        if exists(mets_server_url):
            remove(mets_server_url)

    if exists(WORKSPACE_DIR):
        rmtree(WORKSPACE_DIR, ignore_errors=True)

    copytree(assets.path_to('kant_aufklaerung_1784/data'), WORKSPACE_DIR)
    workspace = Workspace(Resolver(), WORKSPACE_DIR)
    p = Process(target=_start_mets_server, kwargs={'workspace': workspace, 'url': request.param})
    p.start()
    sleep(2)  # sleep to start up server
    yield mets_server_url, Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=mets_server_url)
    p.terminate()
    rmtree(WORKSPACE_DIR, ignore_errors=True)

def add_file_server(x):
    mets_server_url, i = x
    workspace_server = Workspace(resolver=Resolver(), directory=WORKSPACE_DIR, mets_server_url=mets_server_url)
    workspace_server.add_file(local_filename=f'foo{i}', mimetype=MIMETYPE_PAGE, page_id=f'page{1}', file_grp='FOO', file_id=f'FOO_page{i}_foo{i}')

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

    assert set(workspace_server.mets.file_groups) == set( ['OCR-D-IMG', 'OCR-D-GT-PAGE', 'OCR-D-GT-ALTO', 'FOO'])
    assert len(workspace_server.mets.find_all_files(fileGrp='FOO')) == NO_FILES
    assert len(workspace_server.mets.find_all_files(file_grp='FOO')) == NO_FILES

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
    assert str(f) == '<ClientSideOcrdFile fileGrp=OCR-D-IMG, ID=INPUT_0017, mimetype=image/tiff, url=OCR-D-IMG/INPUT_0017.tif, local_filename=OCR-D-IMG/INPUT_0017.tif]/>'
    a = workspace_server.mets.agents[0]
    assert str(a) == '<ClientSideOcrdAgent [type=---, othertype=SOFTWARE, role=CREATOR, otherrole=---, name=DFG-Koordinierungsprojekt zur Weiterentwicklung von Verfahren der Optical Character Recognition (OCR-D)]/>'
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
    assert workspace_server.mets.unique_identifier == 'http://kant_aufklaerung_1784'
