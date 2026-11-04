from typing import Callable, Dict, List, Union

from fastapi import File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from ocrd.task_sequence import ProcessorTask

from ...constants import JobState
from ...database import (
    db_find_first_workflow_script_by_content,
    db_get_processing_jobs,
    db_get_workflow_script,
)
from ...models import DBProcessorJob, DBWorkflowJob, DBWorkflowScript, PYJobInput, PYWorkflowJobOutput
from ...server_utils import (
    create_workspace_if_not_exists,
    get_from_database_workflow_job,
    get_from_database_workspace,
    get_page_ids_list,
    get_workflow_content,
    parse_workflow_tasks,
    send_workflow_callback,
    validate_first_task_input_file_groups_existence,
    validate_workflow,
    raise_http_exception,
)
from ...utils import generate_id, generate_workflow_content, generate_workflow_content_hash


class WorkflowService:
    """Manage workflow parsing, execution, status and workflow scripts."""

    def __init__(
        self, log, processing_job_callback: Callable,
        worker_validation_callback: Callable, stop_mets_server_callback: Callable
    ):
        self.log = log
        self.processing_job_callback = processing_job_callback
        self.worker_validation_callback = worker_validation_callback
        self.stop_mets_server_callback = stop_mets_server_callback

    async def maybe_finish_workflow(self, workflow_job_id: str) -> None:
        workflow_job = await get_from_database_workflow_job(self.log, workflow_job_id)

        if workflow_job.callback_sent:
            return
        if not workflow_job.submission_complete:
            return
        if not workflow_job.mets_server_stopped:
            return

        job_ids = [
            job_id
            for ids in workflow_job.processing_job_ids.values()
            for job_id in ids
        ]
        if not job_ids:
            self.log.warning(f"Workflow {workflow_job_id} has no processing job IDs")
            return

        processing_jobs = await db_get_processing_jobs(job_ids)
        if len(processing_jobs) != len(job_ids):
            self.log.warning(
                f"Workflow {workflow_job_id}: not all processing jobs "
                "are available in the database yet"
            )
            return

        state = self.produce_workflow_status_simple_response(processing_jobs)
        if state not in (JobState.success, JobState.failed):
            return

        delivered = await send_workflow_callback(self.log, workflow_job, state)
        if delivered:
            workflow_job.callback_sent = True
            await workflow_job.save()

    async def task_sequence_to_processing_jobs(
        self, tasks: List[ProcessorTask], mets_path: str, page_id: str
    ):
        temp_file_group_cache = {}
        responses = []

        for task in tasks:
            dependent_jobs = []
            for input_file_grp in task.input_file_grps:
                if input_file_grp in temp_file_group_cache:
                    dependent_jobs.append(temp_file_group_cache[input_file_grp])

            job_input_data = PYJobInput(
                processor_name=task.executable,
                path_to_mets=mets_path,
                input_file_grps=task.input_file_grps,
                output_file_grps=task.output_file_grps,
                page_id=page_id,
                parameters=task.parameters,
                depends_on=dependent_jobs,
            )
            assert job_input_data.processor_name

            response = await self.processing_job_callback(
                processor_name=job_input_data.processor_name,
                data=job_input_data,
            )
            for file_group in task.output_file_grps:
                temp_file_group_cache[file_group] = response.job_id
            responses.append(response)

        return responses

    def validate_tasks_worker_existence(self, tasks: List[ProcessorTask]) -> None:
        missing_workers = []
        for task in tasks:
            try:
                self.worker_validation_callback(processor_name=task.executable)
            except HTTPException:
                missing_workers.append({task.executable})

        if missing_workers:
            message = (
                "Workflow validation has failed. The desired Processing Worker "
                "was not found. Missing Processing Workers: "
                f"{missing_workers}"
            )
            raise_http_exception(self.log, 406, message)

    async def run_workflow(
        self,
        mets_path: str,
        workflow: Union[UploadFile, str, None] = File(None),
        workflow_id: str = None,
        page_id: str = None,
        page_wise: bool = False,
        workflow_callback_url: str = None,
    ) -> PYWorkflowJobOutput:
        await create_workspace_if_not_exists(self.log, mets_path=mets_path)
        workflow_content = await get_workflow_content(self.log, workflow_id, workflow)
        processing_tasks = parse_workflow_tasks(self.log, workflow_content)

        validate_first_task_input_file_groups_existence(
            self.log, mets_path, processing_tasks[0].input_file_grps
        )
        self.validate_tasks_worker_existence(processing_tasks)
        page_id = page_id or ""

        db_workflow_job = DBWorkflowJob(
            job_id=generate_id(),
            page_id=page_id,
            page_wise=page_wise,
            processing_job_ids={},
            path_to_mets=mets_path,
            workflow_callback_url=workflow_callback_url,
        )
        await db_workflow_job.insert()

        if page_wise:
            all_pages_job_ids = {}
            page_ids = get_page_ids_list(self.log, mets_path, page_id)
            for current_page in page_ids:
                responses = await self.task_sequence_to_processing_jobs(
                    tasks=processing_tasks,
                    mets_path=mets_path,
                    page_id=current_page,
                )
                all_pages_job_ids[current_page] = [
                    response.job_id for response in responses
                ]
        else:
            responses = await self.task_sequence_to_processing_jobs(
                tasks=processing_tasks,
                mets_path=mets_path,
                page_id=page_id,
            )
            all_pages_job_ids = {
                page_id: [response.job_id for response in responses]
            }

        db_workflow_job.processing_job_ids = all_pages_job_ids
        db_workflow_job.submission_complete = True
        await db_workflow_job.save()

        db_workspace = await get_from_database_workspace(
            self.log, workspace_mets_path=mets_path
        )
        await self.stop_mets_server_callback(
            workspace_key=mets_path,
            mets_server_url=db_workspace.mets_server_url,
            path_to_mets=mets_path,
        )
        return db_workflow_job.to_job_output()

    @staticmethod
    def produce_workflow_status_response(
        processing_jobs: List[DBProcessorJob]
    ) -> Dict:
        if not processing_jobs:
            return {}

        response = {}
        failed_tasks_key = "failed-processor-tasks"
        failed_tasks = {}

        for p_job in processing_jobs:
            response.setdefault(p_job.processor_name, {})
            response[p_job.processor_name].setdefault(p_job.state.value, 0)
            response[p_job.processor_name][p_job.state.value] += 1

            if p_job.state == JobState.failed:
                response.setdefault(failed_tasks_key, failed_tasks)
                failed_tasks.setdefault(p_job.processor_name, [])
                failed_tasks[p_job.processor_name].append({
                    "job_id": p_job.job_id,
                    "page_id": p_job.page_id,
                })
        return response

    @staticmethod
    def produce_workflow_status_simple_response(
        processing_jobs: List[DBProcessorJob]
    ) -> JobState:
        if not processing_jobs:
            return JobState.unset

        workflow_job_state = JobState.unset
        success_jobs = 0

        for p_job in processing_jobs:
            if p_job.state in (JobState.cached, JobState.queued):
                continue
            if p_job.state in (JobState.failed, JobState.cancelled):
                workflow_job_state = JobState.failed
                break
            if p_job.state == JobState.running:
                workflow_job_state = JobState.running
            if p_job.state == JobState.success:
                success_jobs += 1

        if len(processing_jobs) == success_jobs:
            workflow_job_state = JobState.success
        return workflow_job_state

    async def get_workflow_info(self, workflow_job_id: str) -> Dict:
        workflow_job = await get_from_database_workflow_job(self.log, workflow_job_id)
        job_ids = [
            job_id
            for ids in workflow_job.processing_job_ids.values()
            for job_id in ids
        ]
        jobs = await db_get_processing_jobs(job_ids)
        return self.produce_workflow_status_response(jobs)

    async def get_workflow_info_simple(self, workflow_job_id: str) -> Dict:
        workflow_job = await get_from_database_workflow_job(self.log, workflow_job_id)
        job_ids = [
            job_id
            for ids in workflow_job.processing_job_ids.values()
            for job_id in ids
        ]
        jobs = await db_get_processing_jobs(job_ids)
        state = self.produce_workflow_status_simple_response(jobs)
        return {"state": state}

    async def upload_workflow(self, workflow: Union[UploadFile, str]) -> Dict[str, str]:
        if isinstance(workflow, str):
            with open(workflow) as wf_file:
                workflow_content = wf_file.read()
        else:
            workflow_content = await generate_workflow_content(workflow)

        validate_workflow(self.log, workflow_content)
        content_hash = generate_workflow_content_hash(workflow_content)

        try:
            existing_script = await db_find_first_workflow_script_by_content(content_hash)
            if existing_script:
                message = (
                    "The same workflow script already exists, workflow id: "
                    f"{existing_script.workflow_id}"
                )
                raise_http_exception(self.log, 409, message)
        except ValueError:
            pass

        workflow_id = generate_id()
        db_workflow_script = DBWorkflowScript(
            workflow_id=workflow_id,
            content=workflow_content,
            content_hash=content_hash,
        )
        await db_workflow_script.insert()
        return {"workflow_id": workflow_id}

    async def replace_workflow(self, workflow_id: str, workflow: Union[UploadFile, str]) -> Dict[str, str]:
        try:
            db_workflow_script = await db_get_workflow_script(workflow_id)
            if isinstance(workflow, str):
                with open(workflow) as wf_file:
                    workflow_content = wf_file.read()
            else:
                workflow_content = await generate_workflow_content(workflow)

            validate_workflow(self.log, workflow_content)
            db_workflow_script.content = workflow_content
            db_workflow_script.content_hash = generate_workflow_content_hash(
                workflow_content
            )
            await db_workflow_script.save()
            return {"workflow_id": db_workflow_script.workflow_id}
        except ValueError as error:
            message = f"Workflow script not existing for id '{workflow_id}'."
            raise_http_exception(self.log, 404, message, error)

    async def download_workflow(self, workflow_id: str) -> PlainTextResponse:
        try:
            workflow = await db_get_workflow_script(workflow_id)
            return PlainTextResponse(workflow.content)
        except ValueError as error:
            message = f"Workflow script not existing for id '{workflow_id}'."
            raise_http_exception(self.log, 404, message, error)