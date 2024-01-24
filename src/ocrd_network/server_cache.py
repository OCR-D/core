from __future__ import annotations
from typing import Dict, List
from logging import FileHandler, Formatter

from ocrd_utils import getLogger, LOG_FORMAT
from .database import db_get_processing_job, db_update_processing_job
from .logging import (
    get_cache_locked_pages_logging_file_path,
    get_cache_processing_requests_logging_file_path
)
from .models import PYJobInput, StateEnum

__all__ = [
    'CacheLockedPages',
    'CacheProcessingRequests'
]


class CacheLockedPages:
    def __init__(self) -> None:
        self.log = getLogger("ocrd_network.server_cache.locked_pages")
        log_file = get_cache_locked_pages_logging_file_path()
        log_fh = FileHandler(filename=log_file, mode='a')
        log_fh.setFormatter(Formatter(LOG_FORMAT))
        self.log.addHandler(log_fh)

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
                self.log.debug(f"Locked pages of `{output_fileGrp}`: "
                               f"{self.locked_pages[workspace_key][output_fileGrp]}")
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
        self.log = getLogger("ocrd_network.server_cache.processing_requests")
        log_file = get_cache_processing_requests_logging_file_path()
        log_fh = FileHandler(filename=log_file, mode='a')
        log_fh.setFormatter(Formatter(LOG_FORMAT))
        self.log.addHandler(log_fh)

        # Used for buffering/caching processing requests in the Processing Server
        # Key: `path_to_mets` if already resolved else `workspace_id`
        # Value: Queue that holds PYInputJob elements
        self.processing_requests: Dict[str, List[PYJobInput]] = {}

        # Used for tracking of active processing jobs for a workspace to decide
        # when the shutdown a METS Server instance for that workspace
        # Key: `path_to_mets` if already resolved else `workspace_id`
        # Value: integer which holds the amount of jobs pushed to the RabbitMQ
        # but no internal callback was yet invoked
        self.__processing_counter: Dict[str, int] = {}

    @staticmethod
    async def __check_if_job_deps_met(dependencies: List[str]) -> bool:
        # Check the states of all dependent jobs
        for dependency_job_id in dependencies:
            try:
                dependency_job_state = (await db_get_processing_job(dependency_job_id)).state
            except ValueError:
                # job_id not (yet) in db. Dependency not met
                return False
            # Found a dependent job whose state is not success
            if dependency_job_state != StateEnum.success:
                return False
        return True

    async def consume_cached_requests(self, workspace_key: str) -> List[PYJobInput]:
        if not self.has_workspace_cached_requests(workspace_key=workspace_key):
            self.log.debug(f"No jobs to be consumed for workspace key: {workspace_key}")
            return []
        found_consume_requests = []
        for i, current_element in enumerate(self.processing_requests[workspace_key]):
            # Request has other job dependencies
            if current_element.depends_on:
                satisfied_dependencies = await self.__check_if_job_deps_met(current_element.depends_on)
                if not satisfied_dependencies:
                    continue
            found_consume_requests.append(current_element)
        found_requests = []
        for found_element in found_consume_requests:
            try:
                (self.processing_requests[workspace_key]).remove(found_element)
                # self.log.debug(f"Found cached request to be processed: {found_request}")
                self.log.debug(f"Found cached request: {found_element.processor_name}, {found_element.page_id}, "
                               f"{found_element.job_id}, depends_on: {found_element.depends_on}")
                found_requests.append(found_element)
            except ValueError:
                # The ValueError is not an issue since the
                # element was removed by another instance
                continue
        return found_requests

    def update_request_counter(self, workspace_key: str, by_value: int) -> int:
        """
        A method used to increase/decrease the internal counter of some workspace_key by `by_value`.
        Returns the value of the updated counter.
        """
        # If a record counter of this workspace key does not exist
        # in the requests counter cache yet, create one and assign 0
        if not self.__processing_counter.get(workspace_key, None):
            self.log.debug(f"Creating an internal request counter for workspace key: {workspace_key}")
            self.__processing_counter[workspace_key] = 0
        self.__processing_counter[workspace_key] = self.__processing_counter[workspace_key] + by_value
        return self.__processing_counter[workspace_key]

    def cache_request(self, workspace_key: str, data: PYJobInput):
        # If a record queue of this workspace key does not exist in the requests cache
        if not self.processing_requests.get(workspace_key, None):
            self.log.debug(f"Creating an internal request queue for workspace_key: {workspace_key}")
            self.processing_requests[workspace_key] = []
        self.log.debug(f"Caching request: {data.processor_name}, {data.page_id}, "
                       f"{data.job_id}, depends_on: {data.depends_on}")
        # Add the processing request to the end of the internal queue
        self.processing_requests[workspace_key].append(data)

    async def cancel_dependent_jobs(self, workspace_key: str, processing_job_id: str) -> List[PYJobInput]:
        if not self.has_workspace_cached_requests(workspace_key=workspace_key):
            self.log.debug(f"No jobs to be cancelled for workspace key: {workspace_key}")
            return []
        self.log.debug(f"Cancelling jobs dependent on job id: {processing_job_id}")
        found_cancel_requests = []
        for i, current_element in enumerate(self.processing_requests[workspace_key]):
            if processing_job_id in current_element.depends_on:
                found_cancel_requests.append(current_element)
        cancelled_jobs = []
        for cancel_element in found_cancel_requests:
            try:
                self.processing_requests[workspace_key].remove(cancel_element)
                self.log.debug(f"For job id: `{processing_job_id}`, "
                               f"cancelling: {cancel_element.job_id}")
                cancelled_jobs.append(cancel_element)
                await db_update_processing_job(job_id=cancel_element.job_id, state=StateEnum.cancelled)
                # Recursively cancel dependent jobs for the cancelled job
                recursively_cancelled = await self.cancel_dependent_jobs(
                    workspace_key=workspace_key,
                    processing_job_id=cancel_element.job_id
                )
                # Add the recursively cancelled jobs to the main list of cancelled jobs
                cancelled_jobs.extend(recursively_cancelled)
            except ValueError:
                # The ValueError is not an issue since the
                # element was removed by another instance
                continue
        return cancelled_jobs

    async def is_caching_required(self, job_dependencies: List[str]) -> bool:
        if not len(job_dependencies):
            # no dependencies found
            return False
        if await self.__check_if_job_deps_met(job_dependencies):
            # all dependencies are met
            return False
        return True

    def has_workspace_cached_requests(self, workspace_key: str) -> bool:
        if not self.processing_requests.get(workspace_key, None):
            self.log.debug(f"In processing requests cache, no workspace key found: {workspace_key}")
            return False
        if not len(self.processing_requests[workspace_key]):
            self.log.debug(f"The processing requests cache is empty for workspace key: {workspace_key}")
            return False
        return True
