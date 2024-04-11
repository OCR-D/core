from __future__ import annotations
from typing import Dict, List

from ocrd_utils import getLogger
from .constants import JobState, SERVER_ALL_PAGES_PLACEHOLDER
from .database import db_get_processing_job, db_update_processing_job
from .logging_utils import (
    configure_file_handler_with_formatter,
    get_cache_locked_pages_logging_file_path,
    get_cache_processing_requests_logging_file_path
)
from .models import PYJobInput
from .utils import call_sync


class CacheLockedPages:
    def __init__(self) -> None:
        self.log = getLogger("ocrd_network.server_cache.locked_pages")
        log_file = get_cache_locked_pages_logging_file_path()
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        # Used for keeping track of locked pages for a workspace
        # Key: `path_to_mets` if already resolved else `workspace_id`
        # Value: A dictionary where each dictionary key is the output file group,
        # and the values are list of strings representing the locked pages
        self.locked_pages: Dict[str, Dict[str, List[str]]] = {}
        # Used as a placeholder to lock all pages when no page_id is specified
        self.placeholder_all_pages: str = SERVER_ALL_PAGES_PLACEHOLDER

    def check_if_locked_pages_for_output_file_grps(
        self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]
    ) -> bool:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No entry found in the locked pages cache for workspace key: {workspace_key}")
            return False
        debug_message = f"Caching the received request due to locked output file grp pages."
        for file_group in output_file_grps:
            if file_group in self.locked_pages[workspace_key]:
                if self.placeholder_all_pages in self.locked_pages[workspace_key][file_group]:
                    self.log.debug(debug_message)
                    return True
                if not set(self.locked_pages[workspace_key][file_group]).isdisjoint(page_ids):
                    self.log.debug(debug_message)
                    return True
        return False

    def get_locked_pages(self, workspace_key: str) -> Dict[str, List[str]]:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No locked pages available for workspace key: {workspace_key}")
            return {}
        return self.locked_pages[workspace_key]

    def lock_pages(self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]) -> None:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No entry found in the locked pages cache for workspace key: {workspace_key}")
            self.log.debug(f"Creating an entry in the locked pages cache for workspace key: {workspace_key}")
            self.locked_pages[workspace_key] = {}
        for file_group in output_file_grps:
            if file_group not in self.locked_pages[workspace_key]:
                self.log.debug(f"Creating an empty list for output file grp: {file_group}")
                self.locked_pages[workspace_key][file_group] = []
            # The page id list is not empty - only some pages are in the request
            if page_ids:
                self.log.debug(f"Locking pages for '{file_group}': {page_ids}")
                self.locked_pages[workspace_key][file_group].extend(page_ids)
                self.log.debug(f"Locked pages of '{file_group}': "
                               f"{self.locked_pages[workspace_key][file_group]}")
            else:
                # Lock all pages with a single value
                self.log.debug(f"Locking pages for '{file_group}': {self.placeholder_all_pages}")
                self.locked_pages[workspace_key][file_group].append(self.placeholder_all_pages)

    def unlock_pages(self, workspace_key: str, output_file_grps: List[str], page_ids: List[str]) -> None:
        if not self.locked_pages.get(workspace_key, None):
            self.log.debug(f"No entry found in the locked pages cache for workspace key: {workspace_key}")
            return
        for file_group in output_file_grps:
            if file_group in self.locked_pages[workspace_key]:
                if page_ids:
                    # Unlock the previously locked pages
                    self.log.debug(f"Unlocking pages of '{file_group}': {page_ids}")
                    self.locked_pages[workspace_key][file_group] = \
                        [x for x in self.locked_pages[workspace_key][file_group] if x not in page_ids]
                    self.log.debug(f"Remaining locked pages of '{file_group}': "
                                   f"{self.locked_pages[workspace_key][file_group]}")
                else:
                    # Remove the single variable used to indicate all pages are locked
                    self.log.debug(f"Unlocking all pages for: {file_group}")
                    self.locked_pages[workspace_key][file_group].remove(self.placeholder_all_pages)


class CacheProcessingRequests:
    def __init__(self) -> None:
        self.log = getLogger("ocrd_network.server_cache.processing_requests")
        log_file = get_cache_processing_requests_logging_file_path()
        configure_file_handler_with_formatter(self.log, log_file=log_file, mode="a")

        # Used for buffering/caching processing requests in the Processing Server
        # Key: `path_to_mets` if already resolved else `workspace_id`
        # Value: Queue that holds PYInputJob elements
        self.processing_requests: Dict[str, List[PYJobInput]] = {}

        # Used for tracking of active processing jobs for a workspace to decide
        # when the shutdown a METS Server instance for that workspace
        # Key: `path_to_mets` if already resolved else `workspace_id`
        # Value: integer which holds the amount of jobs pushed to the RabbitMQ
        # but no internal callback was yet invoked
        self.processing_counter: Dict[str, int] = {}

    @staticmethod
    async def __check_if_job_deps_met(dependencies: List[str]) -> bool:
        # Check the states of all dependent jobs
        for dependency_job_id in dependencies:
            try:
                dependency_job_state = (await db_get_processing_job(dependency_job_id)).state
                # Found a dependent job whose state is not success
                if dependency_job_state != JobState.success:
                    return False
            except ValueError:
                # job_id not (yet) in db. Dependency not met
                return False
        return True

    def __print_job_input_debug_message(self, job_input: PYJobInput):
        debug_message = "Processing job input"
        debug_message += f", processor: {job_input.processor_name}"
        debug_message += f", page ids: {job_input.page_id}"
        debug_message += f", job id: {job_input.job_id}"
        debug_message += f", job depends on: {job_input.depends_on}"
        self.log.debug(debug_message)

    async def consume_cached_requests(self, workspace_key: str) -> List[PYJobInput]:
        if not self.has_workspace_cached_requests(workspace_key=workspace_key):
            self.log.debug(f"No jobs to be consumed for workspace key: {workspace_key}")
            return []
        found_consume_requests = []
        for current_element in self.processing_requests[workspace_key]:
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
                self.__print_job_input_debug_message(job_input=found_element)
                found_requests.append(found_element)
            except ValueError:
                # The ValueError is not an issue since the element was removed by another instance
                continue
        return found_requests

    @call_sync
    async def sync_consume_cached_requests(self, workspace_key: str) -> List[PYJobInput]:
        return await self.consume_cached_requests(workspace_key=workspace_key)

    def update_request_counter(self, workspace_key: str, by_value: int) -> int:
        """
        A method used to increase/decrease the internal counter of some workspace_key by `by_value`.
        Returns the value of the updated counter.
        """
        # If a record counter of this workspace key does not exist
        # in the requests counter cache yet, create one and assign 0
        if not self.processing_counter.get(workspace_key, None):
            self.log.debug(f"Creating an internal request counter for workspace key: {workspace_key}")
            self.processing_counter[workspace_key] = 0
        self.processing_counter[workspace_key] = self.processing_counter[workspace_key] + by_value
        return self.processing_counter[workspace_key]

    def cache_request(self, workspace_key: str, data: PYJobInput):
        # If a record queue of this workspace key does not exist in the requests cache
        if not self.processing_requests.get(workspace_key, None):
            self.log.debug(f"Creating an internal request queue for workspace_key: {workspace_key}")
            self.processing_requests[workspace_key] = []
        self.__print_job_input_debug_message(job_input=data)
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
                self.log.debug(f"For job id: '{processing_job_id}', cancelling job id: '{cancel_element.job_id}'")
                cancelled_jobs.append(cancel_element)
                await db_update_processing_job(job_id=cancel_element.job_id, state=JobState.cancelled)
                # Recursively cancel dependent jobs for the cancelled job
                recursively_cancelled = await self.cancel_dependent_jobs(
                    workspace_key=workspace_key, processing_job_id=cancel_element.job_id
                )
                # Add the recursively cancelled jobs to the main list of cancelled jobs
                cancelled_jobs.extend(recursively_cancelled)
            except ValueError:
                # The ValueError is not an issue since the element was removed by another instance
                continue
        return cancelled_jobs

    @call_sync
    async def sync_cancel_dependent_jobs(self, workspace_key: str, processing_job_id: str) -> List[PYJobInput]:
        # A synchronous wrapper around the async method
        return await self.cancel_dependent_jobs(workspace_key=workspace_key, processing_job_id=processing_job_id)

    async def is_caching_required(self, job_dependencies: List[str]) -> bool:
        if not len(job_dependencies):
            return False  # no dependencies found
        if await self.__check_if_job_deps_met(job_dependencies):
            return False  # all dependencies are met
        return True

    @call_sync
    async def sync_is_caching_required(self, job_dependencies: List[str]) -> bool:
        # A synchronous wrapper around the async method
        return await self.is_caching_required(job_dependencies=job_dependencies)

    def has_workspace_cached_requests(self, workspace_key: str) -> bool:
        if not self.processing_requests.get(workspace_key, None):
            self.log.debug(f"In processing requests cache, no workspace key found: {workspace_key}")
            return False
        if not len(self.processing_requests[workspace_key]):
            self.log.debug(f"The processing requests cache is empty for workspace key: {workspace_key}")
            return False
        return True
