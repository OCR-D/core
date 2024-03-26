""" The database is used to store information regarding jobs and workspaces.

Jobs: for every process-request a job is inserted into the database with an uuid, status and
information about the process like parameters and file groups. It is mainly used to track the status
(`ocrd_network.constants.JobState`) of a job so that the state of a job can be queried. Finished
jobs are not deleted from the database.

Workspaces: A job or a processor always runs on a workspace. So a processor needs the information
where the workspace is available. This information can be set with providing an absolute path or a
workspace_id. With the latter, the database is used to convert the workspace_id to a path.

XXX: Currently the information is not preserved after the processing-server shuts down as the
database (runs in docker) currently has no volume set.
"""
from beanie import init_beanie
from beanie.operators import In
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from pymongo import MongoClient, uri_parser as mongo_uri_parser
from re import sub as re_sub
from typing import List
from uuid import uuid4

from .models import DBProcessorJob, DBWorkflowJob, DBWorkspace, DBWorkflowScript
from .utils import call_sync


async def initiate_database(db_url: str, db_name: str = 'ocrd'):
    client = AsyncIOMotorClient(db_url)
    await init_beanie(
        database=client.get_default_database(default=db_name),
        document_models=[DBProcessorJob, DBWorkflowJob, DBWorkspace, DBWorkflowScript]
    )


@call_sync
async def sync_initiate_database(db_url: str, db_name: str = 'ocrd'):
    await initiate_database(db_url, db_name)


async def db_create_workspace(mets_path: str) -> DBWorkspace:
    """ Create a workspace-database entry only from a mets-path
    """
    if not Path(mets_path).exists():
        raise FileNotFoundError(f'Cannot create DB workspace entry, `{mets_path}` does not exist!')
    try:
        return await db_get_workspace(workspace_mets_path=mets_path)
    except ValueError:
        workspace_db = DBWorkspace(
            workspace_id=str(uuid4()),
            workspace_path=Path(mets_path).parent,
            workspace_mets_path=mets_path,
            ocrd_identifier="",
            bagit_profile_identifier="",
        )
        await workspace_db.save()
        return workspace_db


@call_sync
async def sync_db_create_workspace(mets_path: str) -> DBWorkspace:
    return await db_create_workspace(mets_path=mets_path)


async def db_get_workspace(workspace_id: str = None, workspace_mets_path: str = None) -> DBWorkspace:
    workspace = None
    if not workspace_id and not workspace_mets_path:
        raise ValueError(f'Either `workspace_id` or `workspace_mets_path` field must be used as a search key')
    if workspace_id:
        workspace = await DBWorkspace.find_one(
            DBWorkspace.workspace_id == workspace_id
        )
        if not workspace:
            raise ValueError(f'Workspace with id "{workspace_id}" not in the DB.')
    if workspace_mets_path:
        workspace = await DBWorkspace.find_one(
            DBWorkspace.workspace_mets_path == workspace_mets_path
        )
        if not workspace:
            raise ValueError(f'Workspace with path "{workspace_mets_path}" not in the DB.')
    return workspace


@call_sync
async def sync_db_get_workspace(workspace_id: str = None, workspace_mets_path: str = None) -> DBWorkspace:
    return await db_get_workspace(workspace_id=workspace_id, workspace_mets_path=workspace_mets_path)


async def db_update_workspace(workspace_id: str = None, workspace_mets_path: str = None, **kwargs) -> DBWorkspace:
    workspace = None
    if not workspace_id and not workspace_mets_path:
        raise ValueError(f'Either `workspace_id` or `workspace_mets_path` field must be used as a search key')
    if workspace_id:
        workspace = await DBWorkspace.find_one(DBWorkspace.workspace_id == workspace_id)
        if not workspace:
            raise ValueError(f'Workspace with id "{workspace_id}" not in the DB.')
    if workspace_mets_path:
        workspace = await DBWorkspace.find_one(DBWorkspace.workspace_mets_path == workspace_mets_path)
        if not workspace:
            raise ValueError(f'Workspace with path "{workspace_mets_path}" not in the DB.')

    job_keys = list(workspace.__dict__.keys())
    for key, value in kwargs.items():
        if key not in job_keys:
            raise ValueError(f'Field "{key}" is not available.')
        if key == 'workspace_id':
            workspace.workspace_id = value
        elif key == 'workspace_mets_path':
            workspace.workspace_mets_path = value
        elif key == 'ocrd_identifier':
            workspace.ocrd_identifier = value
        elif key == 'bagit_profile_identifier':
            workspace.bagit_profile_identifier = value
        elif key == 'ocrd_base_version_checksum':
            workspace.ocrd_base_version_checksum = value
        elif key == 'ocrd_mets':
            workspace.ocrd_mets = value
        elif key == 'bag_info_adds':
            workspace.bag_info_adds = value
        elif key == 'deleted':
            workspace.deleted = value
        elif key == 'mets_server_url':
            workspace.mets_server_url = value
        else:
            raise ValueError(f'Field "{key}" is not updatable.')
    await workspace.save()
    return workspace


@call_sync
async def sync_db_update_workspace(workspace_id: str = None, workspace_mets_path: str = None, **kwargs) -> DBWorkspace:
    return await db_update_workspace(workspace_id=workspace_id, workspace_mets_path=workspace_mets_path, **kwargs)


async def db_create_processing_job(db_processing_job: DBProcessorJob) -> DBProcessorJob:
    return await db_processing_job.insert()


@call_sync
async def sync_db_create_processing_job(db_processing_job: DBProcessorJob) -> DBProcessorJob:
    return await db_create_processing_job(db_processing_job=db_processing_job)


async def db_get_processing_job(job_id: str) -> DBProcessorJob:
    job = await DBProcessorJob.find_one(
        DBProcessorJob.job_id == job_id)
    if not job:
        raise ValueError(f'Processing job with id "{job_id}" not in the DB.')
    return job


@call_sync
async def sync_db_get_processing_job(job_id: str) -> DBProcessorJob:
    return await db_get_processing_job(job_id)


async def db_update_processing_job(job_id: str, **kwargs) -> DBProcessorJob:
    job = await DBProcessorJob.find_one(
        DBProcessorJob.job_id == job_id)
    if not job:
        raise ValueError(f'Processing job with id "{job_id}" not in the DB.')

    job_keys = list(job.__dict__.keys())
    for key, value in kwargs.items():
        if key not in job_keys:
            raise ValueError(f'Field "{key}" is not available.')
        if key == 'state':
            job.state = value
        elif key == 'start_time':
            job.start_time = value
        elif key == 'end_time':
            job.end_time = value
        elif key == 'path_to_mets':
            job.path_to_mets = value
        elif key == 'exec_time':
            job.exec_time = value
        elif key == 'log_file_path':
            job.log_file_path = value
        else:
            raise ValueError(f'Field "{key}" is not updatable.')
    await job.save()
    return job


@call_sync
async def sync_db_update_processing_job(job_id: str, **kwargs) -> DBProcessorJob:
    return await db_update_processing_job(job_id=job_id, **kwargs)


async def db_create_workflow_job(db_workflow_job: DBWorkflowJob) -> DBWorkflowJob:
    return await db_workflow_job.insert()


@call_sync
async def sync_db_create_workflow_job(db_workflow_job: DBWorkflowJob) -> DBWorkflowJob:
    return await db_create_workflow_job(db_workflow_job=db_workflow_job)


async def db_get_workflow_job(job_id: str) -> DBWorkflowJob:
    job = await DBWorkflowJob.find_one(DBWorkflowJob.job_id == job_id)
    if not job:
        raise ValueError(f'Workflow job with id "{job_id}" not in the DB.')
    return job


@call_sync
async def sync_db_get_workflow_job(job_id: str) -> DBWorkflowJob:
    return await db_get_workflow_job(job_id)


async def db_get_processing_jobs(job_ids: List[str]) -> List[DBProcessorJob]:
    jobs = await DBProcessorJob.find(In(DBProcessorJob.job_id, job_ids)).to_list()
    return jobs


@call_sync
async def sync_db_get_processing_jobs(job_ids: List[str]) -> List[DBProcessorJob]:
    return await db_get_processing_jobs(job_ids)


async def db_create_workflow_script(db_workflow_script: DBWorkflowScript) -> DBWorkflowScript:
    return await db_workflow_script.insert()


@call_sync
async def sync_db_create_workflow_script(db_workflow_script: DBWorkflowScript) -> DBWorkflowScript:
    return await db_create_workflow_script(db_workflow_script=db_workflow_script)


async def db_get_workflow_script(workflow_id: str) -> DBWorkflowScript:
    workflow = await DBWorkflowScript.find_one(DBWorkflowScript.workflow_id == workflow_id)
    if not workflow:
        raise ValueError(f'Workflow-script with id "{workflow_id}" not in the DB.')
    return workflow


@call_sync
async def sync_db_get_workflow_script(workflow_id: str) -> DBWorkflowScript:
    return await db_get_workflow_script(workflow_id)


async def db_find_first_workflow_script_by_content(content_hash: str) -> DBWorkflowScript:
    workflow = await DBWorkflowScript.find_one(DBWorkflowScript.content_hash == content_hash)
    if not workflow:
        raise ValueError(f'Workflow-script with content_hash "{content_hash}" not in the DB.')
    return workflow


# TODO: Resolve the inconsistency between the async and sync versions of the same method
@call_sync
async def sync_db_find_first_workflow_script_by_content(workflow_id: str) -> DBWorkflowScript:
    return await db_get_workflow_script(workflow_id)


def verify_database_uri(mongodb_address: str) -> str:
    try:
        # perform validation check
        mongo_uri_parser.parse_uri(uri=mongodb_address, validate=True)
    except Exception as error:
        raise ValueError(f"The MongoDB address '{mongodb_address}' is in wrong format, {error}")
    return mongodb_address


def verify_mongodb_available(mongo_url: str) -> None:
    """
    # The protocol is intentionally set to HTTP instead of MONGODB!
    mongodb_test_url = mongo_url.replace("mongodb", "http")
    if is_url_responsive(url=mongodb_test_url, tries=3):
        return
    raise RuntimeError(f"Verifying connection has failed: {mongodb_test_url}")
    """

    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=60000.0)
        client.admin.command("ismaster")
    except Exception:
        raise RuntimeError(f'Cannot connect to MongoDB: {re_sub(r":[^@]+@", ":****@", mongo_url)}')