from os import chdir
from os.path import join, exists
from pathlib import Path
from filecmp import dircmp
from shutil import copytree, copy
from io import StringIO
from contextlib import contextmanager
import sys

from click.testing import CliRunner

import pytest

# pylint: disable=import-error, no-name-in-module
from tests.base import CapturingTestCase, assets, copy_of_directory, main, invoke_cli

from ocrd_utils import disableLogging, pushd_popd
from ocrd.cli.workspace import workspace_cli
from ocrd import Resolver

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent


@contextmanager
def mock_stdin(inp):
    old_stdin = sys.stdin
    sys.stdin = StringIO(inp)
    yield
    sys.stdin = old_stdin


def test_add_image_to_workspace(tmp_path):
    """
    Ensure that `ocrd workspace add` does the right thing
    """
    # arrange
    ID = 'foo123file'
    page_id = 'foo123page'
    file_grp = 'TEST_GROUP'
    content = 'x'
    mimetype = 'image/tiff'
    ws_api = Resolver().workspace_from_nothing(directory=tmp_path)
    ws_api.save_mets()
    content_file = join(tmp_path, 'testfile')
    with open(content_file, 'w') as f:
        f.write(content)

    # act
    result = CliRunner(mix_stderr=False).invoke(workspace_cli, [
        '-d', tmp_path,
        'add',
        '--file-grp', file_grp,
        '--page-id', page_id,
        '--file-id', ID,
        '--mimetype', mimetype,
        content_file
    ])

    # assert
    assert result.exit_code == 0


def test_remove_image_from_workspace_but_keep_file(tmp_path):

    # arrange
    ID = 'foo123file'
    page_id = 'foo123page'
    file_grp = 'TEST_GROUP'
    content = 'x'
    mimetype = 'image/tiff'
    content_file = join(tmp_path, 'testfile')
    runner = CliRunner(mix_stderr=False)
    with open(content_file, 'w') as f:
        f.write(content)
    Resolver().workspace_from_nothing(directory=tmp_path).save_mets()
    runner.invoke(workspace_cli, ['init', tmp_path])
    runner.invoke(workspace_cli, [
        '-d', tmp_path,
        'add',
        '--file-grp', file_grp,
        '--page-id', page_id,
        '--file-id', ID,
        '--mimetype', mimetype,
        content_file
    ])

    # act
    result = runner.invoke(workspace_cli, [
        '-d',
        tmp_path,
        'remove',
        '--keep-file',
        ID
    ])

    # asserts
    # cli terminated regulary
    assert result.exit_code == 0
    # File still exists physical
    assert exists(content_file)


def test_remove_image_with_force_deletes_file(tmp_path):

    # arrange
    ID = 'foo123file'
    page_id = 'foo123page'
    file_grp = 'TEST_GROUP'
    content = 'x'
    mimetype = 'image/tiff'
    content_file = join(tmp_path, 'testfile')
    with open(content_file, 'w') as f:
        f.write(content)
    Resolver().workspace_from_nothing(directory=tmp_path).save_mets()
    runner = CliRunner(mix_stderr=False)
    runner.invoke(workspace_cli, [
        '-d', tmp_path,
        'add',
        '--file-grp', file_grp,
        '--page-id', page_id,
        '--file-id', ID,
        '--mimetype', mimetype,
        content_file
    ])

    # act
    result = runner.invoke(workspace_cli, [
        '-d',
        tmp_path,
        'remove',
        '--force',
        ID
    ])
    assert result.exit_code == 0
    # File should have been deleted
    assert not exists(content_file)


def test_add_image_from_url(tmp_path):

    # arrange
    ID = 'foo123file'
    page_id = 'foo123page'
    file_grp = 'TEST_GROUP'
    mimetype = 'image/tiff'
    url = 'http://remote/file.tif'
    ws = Resolver().workspace_from_nothing(directory=tmp_path)
    ws.save_mets()

    # act
    CliRunner(mix_stderr=False).invoke(workspace_cli, [
        '-d', tmp_path,
        'add',
        '--file-grp', file_grp,
        '--page-id', page_id,
        '--file-id', ID,
        '--mimetype', mimetype,
        url])
    ws.reload_mets()
    f = ws.mets.find_all_files()[0]

    # assert
    assert f.url == url


def test_add_nonexisting_file_fails(tmp_path, capfd):
    """TODO log part moved to separate test"""

    # arrange
    ID = 'foo123file'
    page_id = 'foo123page'
    file_grp = 'TEST_GROUP'
    mimetype = 'image/tiff'
    chdir(tmp_path)
    ws = Resolver().workspace_from_nothing(directory=tmp_path)
    ws.save_mets()

    # act
    exit_code, _, _ = invoke_cli(workspace_cli, [
        'add',
        '-C',
        '--file-grp', file_grp,
        '--page-id', page_id,
        '--file-id', ID,
        '--mimetype', mimetype,
        'does-not-exist.xml'], capfd)

    # assert
    assert exit_code == 1


class TestWorkspaceCLIWithStderr(CapturingTestCase):

    def setUp(self):
        super().setUp()
        disableLogging()
        self.maxDiff = None
        self.resolver = Resolver()
        self.runner = CliRunner(mix_stderr=False)

    @pytest.mark.skip(reason="fails when logging conf present in $HOME")
    def test_add_nonexisting_file_fails_logged(self):
        """TODO: unclear how to do in pytest"""

        ID = 'foo123file'
        page_id = 'foo123page'
        file_grp = 'TEST_GROUP'
        mimetype = 'image/tiff'
        with pushd_popd(tempdir=True) as tempdir:
            ws = self.resolver.workspace_from_nothing(directory=tempdir)
            ws.save_mets()
            _, _, err = self.invoke_cli(workspace_cli, [
                '-d', tempdir,
                'add',
                '-C',
                '--file-grp', file_grp,
                '--page-id', page_id,
                '--file-id', ID,
                '--mimetype', mimetype,
                'does-not-exist.xml'])

            assert "File 'does-not-exist.xml' does not exist, halt execution!" in err

    @pytest.mark.skip(reason="fails when logging conf present in $HOME")
    def test_init_with_mets_basename_and_not_mets_deprecated_succeeds_logged(self):
        """TODO: unclear how to do in pytest"""

        # arrange
        with pushd_popd(tempdir=True) as tempdir:

            # act
            _, out, err = self.invoke_cli(workspace_cli, ['-d', 'foo', '-M', 'not-foo.xml', 'init'])

            # assert
            assert str(join(tempdir, 'foo')) in out
            assert '--mets-basename is deprecated' in err


def test_add_file_from_outside_path(tmp_path, capfd):
    """
    https://github.com/OCR-D/core/issues/519
    """

    # arrange
    wsdir = Path(tmp_path, "workspace")
    wsdir.mkdir()
    srcdir = Path(tmp_path, "source")
    srcdir.mkdir()
    srcfile = Path(srcdir, "srcfile.jpg")
    srcfile_content = 'foo'
    srcfile.write_text(srcfile_content)
    chdir(wsdir)
    invoke_cli(workspace_cli, ['init'], capfd)

    # act
    exit_code, _, _ = invoke_cli(workspace_cli, [
        'add',
        '-m', 'image/jpg',
        '-G', 'MAX',
        '-i', 'IMG_MAX_1818975',
        '-C',
        str(srcfile)
    ], capfd)

    # assert
    assert exit_code == 0
    assert Path(wsdir, 'MAX', 'srcfile.jpg').exists()
    assert Path(wsdir, 'MAX', 'srcfile.jpg').read_text() == srcfile_content


def test_add_image_check_exists(tmp_path, capfd):

    # arrange
    ID = 'foo123file'
    page_id = 'foo123page'
    file_grp = 'TEST_GROUP'
    mimetype = 'image/tiff'
    content_file = join(tmp_path, 'test.tif')
    ws = Resolver().workspace_from_nothing(directory=tmp_path)
    ws.save_mets()
    with open(content_file, 'w') as f:
        f.write('x')

    # act
    exit_code, _, _ = invoke_cli(workspace_cli, [
        '-d', tmp_path,
        'add',
        '-C',
        '--file-grp', file_grp,
        '--page-id', page_id,
        '--file-id', ID,
        '--mimetype', mimetype,
        content_file], capfd)

    # assert
    assert exit_code == 0
    ws.reload_mets()
    f = ws.mets.find_all_files()[0]
    assert f.url == 'test.tif'


def test_find_all_files(tmp_path, capfd):
    """Ensure both files are found and printed to stdout
    """

    # arrange
    wsdir = join(tmp_path, 'ws')
    copytree(assets.path_to('SBB0000F29300010000/data'), wsdir)

    # act
    chdir(wsdir)
    exit_code, output, _ = invoke_cli(workspace_cli, ['find', '-G', 'OCR-D-IMG-BIN', '-k', 'fileGrp'], capfd)

    # assert
    assert exit_code == 0
    assert output == 'OCR-D-IMG-BIN\nOCR-D-IMG-BIN\n'


def test_prune_files(tmp_path):

    # arrange
    copytree(assets.path_to('SBB0000F29300010000/data'), join(tmp_path, 'ws'))
    ws1 = Resolver().workspace_from_url(join(tmp_path, 'ws', 'mets.xml'))

    # act
    result = CliRunner().invoke(workspace_cli, ['-d', join(tmp_path, 'ws'), 'prune-files'])

    # assert: workspace mets contained once 35 files
    assert len(ws1.mets.find_all_files()) == 35
    assert result.exit_code == 0

    # just reload present Workspace
    ws1.reload_mets()
    assert len(ws1.mets.find_all_files()) == 7


def test_clone_into_nonexisting_dir(tmp_path):
    """
    https://github.com/OCR-D/core/issues/330
    """
    clone_to = join(tmp_path, 'non-existing-dir')
    result = CliRunner().invoke(workspace_cli, [
        'clone',
        '--download',
        assets.path_to('scribo-test/data/mets.xml'),
        clone_to
    ])
    assert result.exit_code == 0


def test_remove_file_group_fails_for_nonempty(tmp_path):
    """
    Test removal of filegrp fails if workspace not empty TODO no CLI?
    """

    # arrange
    wsdir = join(tmp_path, 'ws')
    copytree(assets.path_to('SBB0000F29300010000/data'), wsdir)
    file_group = 'OCR-D-GT-PAGE'
    file_path = Path(tmp_path, 'ws', file_group, 'FILE_0002_FULLTEXT.xml')
    workspace = Resolver().workspace_from_url(join(wsdir, 'mets.xml'))

    # act
    with pytest.raises(Exception) as exc:
        workspace.remove_file_group(file_group)

    # assert
    assert "not empty" in exc.value.args[0]
    assert file_path.exists()
    assert len(workspace.mets.file_groups) == 17
    assert len(workspace.mets.find_all_files()) == 35


def test_remove_file_group_force(tmp_path):
    """
    Test removal of filegrp TODO no CLI
    """

    # arrange
    wsdir = join(tmp_path, 'ws')
    copytree(assets.path_to('SBB0000F29300010000/data'), wsdir)
    file_group = 'OCR-D-GT-PAGE'
    file_path = Path(tmp_path, 'ws', file_group, 'FILE_0002_FULLTEXT.xml')
    workspace = Resolver().workspace_from_url(join(wsdir, 'mets.xml'))

    # act
    workspace.remove_file_group(file_group, recursive=True, force=True)

    # assert
    assert len(workspace.mets.file_groups) == 16
    assert len(workspace.mets.find_all_files()) == 33
    # TODO changed from assert file_path.exists()
    assert not file_path.exists()
    # TODO ensure empty dirs removed - yes they are, it's done recursive ??
    assert not file_path.parent.exists()


def test_clone_relative(tmp_path):
    """
    Create a relative path to trigger make sure #319 is gone
    changing the current dir is cruical to assert relative paths
    """

    # arrange
    chdir(PROJECT_ROOT_DIR)
    src_path = str(Path(assets.path_to('kant_aufklaerung_1784/data/mets.xml')).relative_to(Path.cwd()))

    # act
    result = CliRunner().invoke(workspace_cli, ['clone', '-a', src_path, str(tmp_path)])

    # assert
    assert result.exit_code == 0
    assert exists(join(tmp_path, 'OCR-D-GT-PAGE/PAGE_0017_PAGE.xml'))


def test_copy_vs_clone(tmp_path):

    # arrange
    src_dir = assets.path_to('kant_aufklaerung_1784/data')
    # cloned without download
    shallowcloneddir = join(tmp_path, 'cloned-shallow')
    # cloned with download
    fullcloneddir = join(tmp_path, 'cloned-all')
    # copied
    copieddir = join(tmp_path, 'copied')
    Path(fullcloneddir).mkdir()
    Path(shallowcloneddir).mkdir()

    # act 1
    result = CliRunner().invoke(workspace_cli, ['clone', join(src_dir, 'mets.xml'), shallowcloneddir])
    assert result.exit_code == 0

    # act 2
    result = CliRunner().invoke(workspace_cli, ['clone', '-a', join(src_dir, 'mets.xml'), fullcloneddir])
    assert result.exit_code == 0

    # assert
    with copy_of_directory(src_dir, copieddir):
        shallow_vs_copied = dircmp(shallowcloneddir, copieddir)
        assert set(shallow_vs_copied.right_only) == set(['OCR-D-GT-ALTO', 'OCR-D-GT-PAGE', 'OCR-D-IMG'])
        full_vs_copied = dircmp(fullcloneddir, copieddir)
        assert full_vs_copied.left_only == []
        assert full_vs_copied.right_only == []


def test_find_all_files_multiple_physical_pages_for_fileids(tmp_path):

    # arrange
    with copy_of_directory(assets.path_to('SBB0000F29300010000/data'), tmp_path) as tempdir:

        # act
        result = CliRunner().invoke(workspace_cli, ['-d', tempdir, 'find', '--page-id', 'PHYS_0005,PHYS_0005', '-k', 'url'])

        # assert
        assert result.stdout == 'OCR-D-IMG/FILE_0005_IMAGE.tif\n'
        assert result.exit_code == 0
        result = CliRunner().invoke(workspace_cli, ['-d', tempdir, 'find', '--page-id', 'PHYS_0005,PHYS_0001', '-k', 'url'])
        assert len(result.stdout.split('\n')) == 19


def test_init_mets_basename(tmp_path):

    # arrange
    chdir(tmp_path)

    # act
    result = CliRunner().invoke(workspace_cli, ['-m', 'foo.xml', 'init'])

    # assert
    assert result.exit_code == 0
    assert exists('foo.xml')
    assert not exists('mets.xml')


def test_init_with_mets_basename_and_mets_raises_valueerror(tmp_path, capfd):

    # arrange
    chdir(tmp_path)

    # act
    with pytest.raises(ValueError) as val_err:
        invoke_cli(workspace_cli, ['-m', 'foo.xml', '-M', 'not-foo.xml', 'init'], capfd)

    # act
    assert "Use either --mets or --mets-basename, not both" in val_err.value.args[0]


def test_init_with_mets_basename_and_not_mets_deprecated_succeeds(tmp_path, capfd):
    """
    TODO altered name, was: test_mets_basename_and_not_mets
    splitted test => 
    """

    # arrange
    src = Path(PROJECT_ROOT_DIR, 'ocrd_utils', 'ocrd_logging.conf')
    dst = Path(tmp_path, 'ocrd_logging.conf')
    copy(src, dst)
    chdir(tmp_path)
    exit_code, _, _ = invoke_cli(workspace_cli, ['-d', 'foo', '-M', 'not-foo.xml', 'init'], capfd)

    # asserts
    assert exit_code == 0


def test_mets_get_id_set_id(tmp_path, capfd):

    # arrange
    chdir(tmp_path)

    # act
    invoke_cli(workspace_cli, ['init'], capfd)
    disableLogging()
    mets_id = 'foo123'
    invoke_cli(workspace_cli, ['set-id', mets_id], capfd)
    disableLogging()
    _, out, _ = invoke_cli(workspace_cli, ['get-id'], capfd)

    assert out == mets_id + '\n'


def test_mets_directory_incompatible(tmp_path, capfd):

    # arrange
    chdir(tmp_path)

    # act
    with pytest.raises(ValueError) as val_err:
        invoke_cli(workspace_cli, ['-d', 'foo', '-m', '/somewhere/else', 'init'], capfd)

    assert "inconsistent with --directory" in val_err.value.args[0]


def test_mets_directory_http(tmp_path, capfd):

    # arrange
    chdir(tmp_path)
    the_url = 'https://foo.bar/bla'

    # act
    with pytest.raises(ValueError) as val_err:
        invoke_cli(workspace_cli, ['-m', the_url, 'init'], capfd)

    assert "--mets is an http(s) URL but no --directory was given" in val_err.value.args[0]


def test_bulk_add0(tmp_path, capfd):
    # arrange data source
    N_FILES = 100
    source_root = Path(tmp_path, "source")
    source_root.mkdir()
    source_img = Path(source_root, "OCR-D-IMG")
    source_img.mkdir()
    # Path(source_root, "OCR-D-PAGE").mkdir()
    for i in range(N_FILES):
        Path(source_img, "page_%04d.tif" % i).write_text('')
    source_pg = Path(source_root, "OCR-D-PAGE")
    source_pg.mkdir()
    for i in range(N_FILES):
        Path(source_pg, "page_%04d.xml" % i).write_text('')

    # arrange
    target_root = Path(tmp_path, "target")
    target_root.mkdir()

    chdir(target_root)
    ws = Resolver().workspace_from_nothing(directory=target_root)
    exit_code, out, err = invoke_cli(workspace_cli, [
        'bulk-add',
        '--ignore',
        '--regex', r'^.*/(?P<fileGrp>[^/]+)/page_(?P<pageid>.*)\.(?P<ext>[^\.]*)$',
        '--url', '{{ fileGrp }}/FILE_{{ pageid }}.{{ ext }}',
        '--file-id', 'FILE_{{ fileGrp }}_{{ pageid }}',
        '--page-id', 'PHYS_{{ pageid }}',
        '--file-grp', '{{ fileGrp }}',
        '%s/*/*' % source_root
    ], capfd)
    ws.reload_mets()
    assert len(ws.mets.file_groups) == 2
    assert len(ws.mets.find_all_files()) == 2 * N_FILES
    assert len(ws.mets.find_all_files(mimetype='image/tiff')) == N_FILES
    assert len(ws.mets.find_all_files(ID='//FILE_OCR-D-IMG_000.*')) == 10
    assert len(ws.mets.find_all_files(ID='//FILE_.*_000.*')) == 20
    assert len(ws.mets.find_all_files(pageId='PHYS_0001')) == 2
    assert ws.mets.find_all_files(ID='FILE_OCR-D-PAGE_0001')[0].url == 'OCR-D-PAGE/FILE_0001.xml'


def test_bulk_add_missing_param(tmp_path, capfd):
    # arrange
    chdir(tmp_path)
    Resolver().workspace_from_nothing(directory=tmp_path)

    # act
    with pytest.raises(ValueError, match=r"OcrdFile attribute 'pageId' unset"):
        invoke_cli(workspace_cli, [
            'bulk-add',
            '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<fileid>.*) (?P<src>.*) (?P<url>.*) (?P<mimetype>.*)',
            '-G', '{{ filegrp }}',
            '-i', '{{ fileid }}',
            '-m', '{{ mimetype }}',
            '-u', "{{ url }}",
            'a b c d e f', '1 2 3 4 5 6'], capfd)


def test_bulk_add_gen_id(tmp_path, capfd):

    # arrange
    chdir(tmp_path)
    ws = Resolver().workspace_from_nothing(directory=tmp_path)
    Path(tmp_path, 'c').write_text('')

    # arrange
    invoke_cli(workspace_cli, [
        'bulk-add',
        '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<src>.*) (?P<url>.*) (?P<mimetype>.*)',
        '-G', '{{ filegrp }}',
        '-g', '{{ pageid }}',
        '-S', '{{ src }}',
        '-m', '{{ mimetype }}',
        '-u', "{{ url }}",
        'a b c d e'], capfd)
    ws.reload_mets()

    # assert
    assert next(ws.mets.find_files()).ID == 'a.b.c.d.e'
    assert next(ws.mets.find_files()).url == 'd'


def test_bulk_add_derive_url(tmp_path, capfd):

    # arrange
    chdir(tmp_path)
    ws = Resolver().workspace_from_nothing(directory=tmp_path)
    Path(tmp_path, 'srcdir').mkdir()
    Path(tmp_path, 'srcdir', 'src.xml').write_text('')

    # act
    CliRunner().invoke(workspace_cli, [
        'bulk-add',
        '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<src>.*)',
        '-G', '{{ filegrp }}',
        '-g', '{{ pageid }}',
        '-S', '{{ src }}',
        'p0001 SEG srcdir/src.xml'])
    ws.reload_mets()

    # assert
    assert next(ws.mets.find_files()).url == 'srcdir/src.xml'


def test_bulk_add_stdin(tmp_path, capfd):

    # arrange
    chdir(tmp_path)
    ws = Resolver().workspace_from_nothing(directory=tmp_path)
    Path(tmp_path, 'BIN').mkdir()
    Path(tmp_path, 'BIN/FILE_0001_BIN.IMG-wolf.png').write_text('')
    Path(tmp_path, 'BIN/FILE_0002_BIN.IMG-wolf.png').write_text('')
    Path(tmp_path, 'BIN/FILE_0001_BIN.xml').write_text('')
    Path(tmp_path, 'BIN/FILE_0002_BIN.xml').write_text('')
    with mock_stdin(
            'PHYS_0001 BIN FILE_0001_BIN.IMG-wolf BIN/FILE_0001_BIN.IMG-wolf.png BIN/FILE_0001_BIN.IMG-wolf.png image/png\n'
            'PHYS_0002 BIN FILE_0002_BIN.IMG-wolf BIN/FILE_0002_BIN.IMG-wolf.png BIN/FILE_0002_BIN.IMG-wolf.png image/png\n'
            'PHYS_0001 BIN FILE_0001_BIN BIN/FILE_0001_BIN.xml BIN/FILE_0001_BIN.xml application/vnd.prima.page+xml\n'
            'PHYS_0002 BIN FILE_0002_BIN BIN/FILE_0002_BIN.xml BIN/FILE_0002_BIN.xml application/vnd.prima.page+xml\n'):
        assert len(ws.mets.file_groups) == 0

        # act
        invoke_cli(workspace_cli, [
            'bulk-add',
            '-r', r'(?P<pageid>.*) (?P<filegrp>.*) (?P<fileid>.*) (?P<src>.*) (?P<dest>.*) (?P<mimetype>.*)',
            '-G', '{{ filegrp }}',
            '-g', '{{ pageid }}',
            '-i', '{{ fileid }}',
            '-m', '{{ mimetype }}',
            '-u', "{{ dest }}",
            '-'], capfd)
        ws.reload_mets()
        assert len(ws.mets.file_groups) == 1
        assert len(list(ws.mets.find_files())) == 4
        f = next(ws.mets.find_files())
        assert f.mimetype == 'image/png'
        assert f.ID == 'FILE_0001_BIN.IMG-wolf'
        assert f.url == 'BIN/FILE_0001_BIN.IMG-wolf.png'


if __name__ == '__main__':
    main(__file__)
