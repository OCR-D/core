from __future__ import annotations
from typing import Dict, List
from logging import DEBUG, getLogger

__all__ = [
    'CacheLockedPages',
    'CacheProcessingRequests'
]


class CacheLockedPages:
    def __init__(self) -> None:
        self.log = getLogger(__name__)
        # TODO: remove this when refactoring the logging
        self.log.setLevel(DEBUG)

        # Used for keeping track of locked pages for a workspace
        # Key: `path_to_mets` if already resolved else `workspace_id`
        # Value: A dictionary where each dictionary key is the output file group,
        # and the values are list of strings representing the locked pages
        self.locked_pages: Dict[str, Dict[str, List[str]]] = {}
        # Used as a placeholder to lock all pages when no page_id is specified
        self.placeholder_all_pages: str = "all_pages"

    def check_if_locked_pages_for_output_file_grps(
            self,
            workspace_key: str,
            output_file_grps: List[str],
            page_ids: List[str]
    ) -> bool:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No entry found in the locked pages cache for workspace key: {workspace_key}")
            return False
        for output_fileGrp in output_file_grps:
            if output_fileGrp in self.locked_pages[workspace_key]:
                if self.placeholder_all_pages in self.locked_pages[workspace_key][output_fileGrp]:
                    self.log.debug(f"Caching the received request due to locked output file grp pages")
                    return True
                if not set(self.locked_pages[workspace_key][output_fileGrp]).isdisjoint(page_ids):
                    self.log.debug(f"Caching the received request due to locked output file grp pages")
                    return True
        return False

    def get_locked_pages(
            self,
            workspace_key: str
    ) -> Dict[str, List[str]]:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No locked pages available for workspace key: {workspace_key}")
            return {}
        return self.locked_pages[workspace_key]

    def lock_pages(
            self,
            workspace_key: str,
            output_file_grps: List[str],
            page_ids: List[str]
    ) -> None:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No entry found in the locked pages cache for workspace key: {workspace_key}")
            self.log.debug(f"Creating an entry in the locked pages cache for workspace key: {workspace_key}")
            self.locked_pages[workspace_key] = {}

        for output_fileGrp in output_file_grps:
            if output_fileGrp not in self.locked_pages[workspace_key]:
                self.log.debug(f"Creating an empty list for output file grp: {output_fileGrp}")
                self.locked_pages[workspace_key][output_fileGrp] = []
            # The page id list is not empty - only some pages are in the request
            if page_ids:
                self.log.debug(f"Locking pages for `{output_fileGrp}`: {page_ids}")
                self.locked_pages[workspace_key][output_fileGrp].extend(page_ids)
            else:
                # Lock all pages with a single value
                self.log.debug(f"Locking pages for `{output_fileGrp}`: {self.placeholder_all_pages}")
                self.locked_pages[workspace_key][output_fileGrp].append(self.placeholder_all_pages)

    def unlock_pages(
            self,
            workspace_key: str,
            output_file_grps: List[str],
            page_ids: List[str]
    ) -> None:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No entry found in the locked pages cache for workspace key: {workspace_key}")
            return
        for output_fileGrp in output_file_grps:
            if output_fileGrp in self.locked_pages[workspace_key]:
                if page_ids:
                    # Unlock the previously locked pages
                    self.log.debug(f"Unlocking pages of `{output_fileGrp}`: {page_ids}")
                    self.locked_pages[workspace_key][output_fileGrp] = \
                        [x for x in self.locked_pages[workspace_key][output_fileGrp] if x not in page_ids]
                    self.log.debug(f"Remaining locked pages of `{output_fileGrp}`: "
                                   f"{self.locked_pages[workspace_key][output_fileGrp]}")
                else:
                    # Remove the single variable used to indicate all pages are locked
                    self.log.debug(f"Unlocking all pages for: {output_fileGrp}")
                    self.locked_pages[workspace_key][output_fileGrp].remove(self.placeholder_all_pages)


class CacheProcessingRequests:
    def __init__(self) -> None:
        pass
