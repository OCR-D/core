""" The database is used to store information regarding jobs and workspaces.

Jobs: for every process-request a job is inserted into the database with a uuid, status and
information about the process like parameters and file groups. It is mainly used to track the status
(`ocrd_network.models.job.StateEnum`) of a job so that the state of a job can be queried. Finished
jobs are not deleted from the database.

Workspaces: A job or a processor always runs on a workspace. So a processor needs the information
where the workspace is available. This information can be set with providing an absolute path or a
workspace_id. With the latter, the database is used to convert the workspace_id to a path.

XXX: Currently the information is not preserved after the processing-server shuts down as the
database (runs in docker) currently has no volume set.
"""
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models import (
    DBProcessorJob,
    DBWorkspace,
    StateEnum
)
from .utils import call_sync


async def initiate_database(db_url: str):
    client = AsyncIOMotorClient(db_url)
    await init_beanie(
        database=client.get_default_database(default='ocrd'),
        document_models=[DBProcessorJob, DBWorkspace]
    )


@call_sync
async def sync_initiate_database(db_url: str):
    await initiate_database(db_url)


async def db_get_workspace(workspace_id: str) -> DBWorkspace:
    workspace = await DBWorkspace.find_one(
        DBWorkspace.workspace_id == workspace_id
    )
    if not workspace:
        raise ValueError(f'Workspace with id "{workspace_id}" not in the DB.')
    return workspace


@call_sync
async def sync_db_get_workspace(workspace_id: str) -> DBWorkspace:
    return await db_get_workspace(workspace_id)


async def db_get_processing_job(job_id: str) -> DBProcessorJob:
    job = await DBProcessorJob.find_one(
        DBProcessorJob.job_id == job_id)
    if not job:
        raise ValueError(f'Processing job with id "{job_id}" not in the DB.')
    return job


async def set_processing_job_state(job_id: str, job_state: StateEnum):
    job = await DBProcessorJob.find_one(
        DBProcessorJob.job_id == job_id)
    if not job:
        raise ValueError(f'Processing job with id "{job_id}" not in the DB.')
    job.state = job_state
    await job.save()


@call_sync
async def sync_set_processing_job_state(job_id: str, job_state: StateEnum):
    await set_processing_job_state(job_id, job_state)


async def get_processing_job_state(job_id: str) -> StateEnum:
    job = await DBProcessorJob.find_one(
        DBProcessorJob.job_id == job_id)
    if not job:
        raise ValueError(f'Processing job with id "{job_id}" not in the DB.')
    return job.state


@call_sync
async def sync_get_processing_job_state(job_id: str) -> StateEnum:
    return await get_processing_job_state(job_id)
