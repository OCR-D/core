from typing import List
from src.ocrd_network.server_cache import CacheLockedPages


def assert_locked_all_pages(pages_cache: CacheLockedPages, workspace_key: str, output_file_grps: List[str]):
    assert len(pages_cache.locked_pages) == 1
    ws_locked_pages_dict = pages_cache.locked_pages[workspace_key]
    assert len(ws_locked_pages_dict) == len(output_file_grps)
    for output_file_group in output_file_grps:
        # The array contains a single element - the placeholder indicating all pages
        assert len(ws_locked_pages_dict[output_file_group]) == 1
        assert ws_locked_pages_dict[output_file_group][0] == pages_cache.placeholder_all_pages


def assert_unlocked_all_pages(pages_cache: CacheLockedPages, workspace_key: str, output_file_grps: List[str]):
    assert len(pages_cache.locked_pages) == 1
    assert len(pages_cache.locked_pages[workspace_key]) == len(output_file_grps)
    for output_file_group in output_file_grps:
        assert len(pages_cache.locked_pages[workspace_key][output_file_group]) == 0


def assert_locked_some_pages(
    pages_cache: CacheLockedPages, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
):
    assert len(pages_cache.locked_pages) == 1
    ws_locked_pages_dict = pages_cache.locked_pages[workspace_key]
    assert len(ws_locked_pages_dict) == len(output_file_grps)
    for output_file_group in output_file_grps:
        assert len(ws_locked_pages_dict[output_file_group]) == len(page_ids)
        for page_id in page_ids:
            assert ws_locked_pages_dict[output_file_group].count(page_id) == 1


def assert_unlocked_some_pages(
    pages_cache: CacheLockedPages, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
):
    assert len(pages_cache.locked_pages) == 1
    ws_locked_pages_dict = pages_cache.locked_pages[workspace_key]
    assert len(ws_locked_pages_dict) == len(output_file_grps)
    for output_file_group in output_file_grps:
        assert len(ws_locked_pages_dict[output_file_group]) == 0
        for page_id in page_ids:
            assert ws_locked_pages_dict[output_file_group].count(page_id) == 0


def test_lock_all_pages():
    workspace_key: str = "test_workspace"
    output_file_grps: List[str] = ["OCR-D-IMG", "OCR-D-BIN"]

    pages_cache = CacheLockedPages()
    pages_cache.lock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=[])
    assert_locked_all_pages(pages_cache, workspace_key, output_file_grps)


def test_unlock_all_pages():
    workspace_key: str = "test_workspace"
    output_file_grps: List[str] = ["OCR-D-IMG", "OCR-D-BIN"]

    pages_cache = CacheLockedPages()
    pages_cache.lock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=[])
    assert_locked_all_pages(pages_cache, workspace_key, output_file_grps)
    pages_cache.unlock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=[])
    assert_unlocked_all_pages(pages_cache, workspace_key, output_file_grps)


def test_lock_some_pages():
    workspace_key: str = "test_workspace"
    # Output file groups whose pages are to be locked
    output_file_grps: List[str] = ["OCR-D-IMG", "OCR-D-BIN"]
    # Pages to be locked for each output file group
    page_ids: List[str] = ["PHYS_0001", "PHYS_0002", "PHYS_0003", "PHYS_0004"]

    pages_cache = CacheLockedPages()
    pages_cache.lock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=page_ids)
    assert_locked_some_pages(pages_cache, workspace_key, output_file_grps, page_ids)


def test_unlock_some_pages():
    workspace_key: str = "test_workspace"
    # Output file groups whose pages are to be locked
    output_file_grps: List[str] = ["OCR-D-IMG", "OCR-D-BIN"]
    # Pages to be locked for each output file group
    page_ids: List[str] = ["PHYS_0001", "PHYS_0002", "PHYS_0003", "PHYS_0004"]

    pages_cache = CacheLockedPages()
    pages_cache.lock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=page_ids)
    assert_locked_some_pages(pages_cache, workspace_key, output_file_grps, page_ids)
    pages_cache.unlock_pages(workspace_key, output_file_grps, page_ids)
    assert_unlocked_some_pages(pages_cache, workspace_key, output_file_grps, page_ids)


def test_get_locked_pages():
    workspace_key: str = "test_workspace"
    # Output file groups whose pages are to be locked
    output_file_grps: List[str] = ["OCR-D-IMG", "OCR-D-BIN"]
    # Pages to be locked for each output file group
    page_ids: List[str] = ["PHYS_0001", "PHYS_0002", "PHYS_0003", "PHYS_0004"]

    pages_cache = CacheLockedPages()
    pages_cache.lock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=page_ids)
    assert_locked_some_pages(pages_cache, workspace_key, output_file_grps, page_ids)
    assert pages_cache.get_locked_pages(workspace_key=workspace_key) == pages_cache.locked_pages[workspace_key]


def test_check_if_locked_pages_for_output_file_grps():
    workspace_key: str = "test_workspace"
    # Output file groups whose pages are to be locked
    output_file_grps: List[str] = ["OCR-D-IMG", "OCR-D-BIN"]
    # Pages to be locked for each output file group
    page_ids: List[str] = ["PHYS_0001", "PHYS_0002", "PHYS_0003", "PHYS_0004"]

    pages_cache = CacheLockedPages()
    pages_cache.lock_pages(workspace_key=workspace_key, output_file_grps=output_file_grps, page_ids=page_ids)
    assert_locked_some_pages(pages_cache, workspace_key, output_file_grps, page_ids)

    # Test for locked pages
    assert pages_cache.check_if_locked_pages_for_output_file_grps(
        workspace_key, output_file_grps=["OCR-D-IMG"], page_ids=["PHYS_0001", "PHYS_0002"]
    )
    assert pages_cache.check_if_locked_pages_for_output_file_grps(
        workspace_key, output_file_grps=["OCR-D-BIN"], page_ids=["PHYS_0003", "PHYS_0004"]
    )

    # Test for non-locked pages
    assert not pages_cache.check_if_locked_pages_for_output_file_grps(
        workspace_key, output_file_grps=["OCR-D-IMG"], page_ids=["PHYS_0010", "PHYS_0011"]
    )
    assert not pages_cache.check_if_locked_pages_for_output_file_grps(
        workspace_key, output_file_grps=["OCR-D-BIN"], page_ids=["PHYS_0010", "PHYS_0011"]
    )

    # Test for non-existing output file group
    assert not pages_cache.check_if_locked_pages_for_output_file_grps(
        workspace_key, output_file_grps=["OCR-D-OCR"], page_ids=["PHYS_0001", "PHYS_0002"]
    )
