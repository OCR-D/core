"""The database stores information regarding jobs and workspaces.

Jobs: For every process request, a job is inserted into the database with a UUID, status and
information about the process, such as parameters and file groups. It is mainly used to track the
status (`ocrd_network.constants.JobState`) of a job so that its state can be queried. Finished
jobs are not deleted from the database.

Workspaces: A job or processor always runs on a workspace. A processor therefore needs to know
where the workspace is available. This information can be set by providing an absolute path or a
workspace_id. With the latter, the database converts the workspace_id to a path.

XXX: Currently the information is not preserved after the processing-server shuts down as the
database (runs in Docker) currently has no volume set.
"""
from pathlib import Path
from re import sub as re_sub
from typing import List
from uuid import uuid4

from beanie import init_beanie
from beanie.operators import In
from pymongo import AsyncMongoClient, MongoClient, ReturnDocument, uri_parser as mongo_uri_parser

from .models import DBProcessorJob, DBWorkflowJob, DBWorkflowScript, DBWorkspace
from .utils import call_sync


UPDATABLE_WORKSPACE_FIELDS = {
    "workspace_id", "workspace_mets_path", "ocrd_identifier", "bagit_profile_identifier",
    "ocrd_base_version_checksum", "ocrd_mets", "bag_info_adds", "deleted", "mets_server_url",
}
UPDATABLE_PROCESSING_JOB_FIELDS = {
    "state", "start_time", "end_time", "path_to_mets", "exec_time", "log_file_path",
}


async def _get_document(model, query, error_message):
    document = await model.find_one(query)
    if not document:
        raise ValueError(error_message)
    return document


async def _update_document(document, updates, updatable_fields):
    document_keys = document.__dict__.keys()
    for key, value in updates.items():
        if key not in document_keys:
            raise ValueError(f'Field "{key}" is not available.')
        if key not in updatable_fields:
            raise ValueError(f'Field "{key}" is not updatable.')
        setattr(document, key, value)
    await document.save()
    return document


# Database initialization

async def initiate_database(db_url: str, db_name: str = 'ocrd'):
    client = AsyncMongoClient(db_url)
    await init_beanie(
        database=client.get_default_database(default=db_name),
        document_models=[DBProcessorJob, DBWorkflowJob, DBWorkspace, DBWorkflowScript]
    )


@call_sync
async def sync_initiate_database(db_url: str, db_name: str = 'ocrd'):
    await initiate_database(db_url, db_name)


# Workspace operations

async def db_create_workspace(mets_path: str) -> DBWorkspace:
    """Create a workspace-database entry only from a mets-path."""
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
    if not workspace_id and not workspace_mets_path:
        raise ValueError('Either `workspace_id` or `workspace_mets_path` field must be used as a search key')
    workspace = None
    if workspace_id:
        workspace = await _get_document(
            DBWorkspace, DBWorkspace.workspace_id == workspace_id,
            f'Workspace with id "{workspace_id}" not in the DB.',
        )
    if workspace_mets_path:
        workspace = await _get_document(
            DBWorkspace, DBWorkspace.workspace_mets_path == workspace_mets_path,
            f'Workspace with path "{workspace_mets_path}" not in the DB.',
        )
    return workspace


@call_sync
async def sync_db_get_workspace(workspace_id: str = None, workspace_mets_path: str = None) -> DBWorkspace:
    return await db_get_workspace(workspace_id=workspace_id, workspace_mets_path=workspace_mets_path)


async def db_update_workspace(workspace_id: str = None, workspace_mets_path: str = None, **kwargs) -> DBWorkspace:
    workspace = None
    if not workspace_id and not workspace_mets_path:
        raise ValueError('Either `workspace_id` or `workspace_mets_path` field must be used as a search key')
    if workspace_id:
        workspace = await _get_document(
            DBWorkspace, DBWorkspace.workspace_id == workspace_id,
            f'Workspace with id "{workspace_id}" not in the DB.',
        )
    if workspace_mets_path:
        workspace = await _get_document(
            DBWorkspace, DBWorkspace.workspace_mets_path == workspace_mets_path,
            f'Workspace with path "{workspace_mets_path}" not in the DB.',
        )
    return await _update_document(workspace, kwargs, UPDATABLE_WORKSPACE_FIELDS)


@call_sync
async def sync_db_update_workspace(workspace_id: str = None, workspace_mets_path: str = None, **kwargs) -> DBWorkspace:
    return await db_update_workspace(workspace_id=workspace_id, workspace_mets_path=workspace_mets_path, **kwargs)


# Processing job operations

async def db_create_processing_job(db_processing_job: DBProcessorJob) -> DBProcessorJob:
    return await db_processing_job.insert()


@call_sync
async def sync_db_create_processing_job(db_processing_job: DBProcessorJob) -> DBProcessorJob:
    return await db_create_processing_job(db_processing_job=db_processing_job)


async def db_get_processing_job(job_id: str) -> DBProcessorJob:
    return await _get_document(
        DBProcessorJob, DBProcessorJob.job_id == job_id,
        f'Processing job with id "{job_id}" not in the DB.'
    )


@call_sync
async def sync_db_get_processing_job(job_id: str) -> DBProcessorJob:
    return await db_get_processing_job(job_id)


async def db_update_processing_job(job_id: str, **kwargs) -> DBProcessorJob:
    job = await db_get_processing_job(job_id)
    return await _update_document(job, kwargs, UPDATABLE_PROCESSING_JOB_FIELDS)


@call_sync
async def sync_db_update_processing_job(job_id: str, **kwargs) -> DBProcessorJob:
    return await db_update_processing_job(job_id=job_id, **kwargs)


async def db_get_processing_jobs(job_ids: List[str]) -> List[DBProcessorJob]:
    return await DBProcessorJob.find(In(DBProcessorJob.job_id, job_ids)).to_list()


@call_sync
async def sync_db_get_processing_jobs(job_ids: List[str]) -> List[DBProcessorJob]:
    return await db_get_processing_jobs(job_ids)


# Processing job callbacks

async def db_claim_result_callback(job_id: str) -> bool:
    """Atomically claim a result callback for processing."""
    result = await DBProcessorJob.get_pymongo_collection().find_one_and_update(
        {
            "job_id": job_id,
            "result_callback_processed": {"$ne": True},
            "result_callback_in_progress": {"$ne": True},
        },
        {"$set": {"result_callback_in_progress": True}},
        return_document=ReturnDocument.BEFORE,
    )
    return result is not None


async def db_claim_result_counter_decrement(job_id: str) -> bool:
    """Atomically claim the result callback's counter decrement."""
    result = await DBProcessorJob.get_pymongo_collection().find_one_and_update(
        {
            "job_id": job_id,
            "result_callback_counter_decremented": {"$ne": True},
        },
        {"$set": {"result_callback_counter_decremented": True}},
        return_document=ReturnDocument.BEFORE,
    )
    return result is not None


async def db_release_result_callback_claim(job_id: str) -> None:
    """Release an in-progress callback claim after processing fails."""
    await DBProcessorJob.get_pymongo_collection().update_one(
        {
            "job_id": job_id,
            "result_callback_processed": {"$ne": True},
        },
        {"$set": {"result_callback_in_progress": False}},
    )


async def db_complete_result_callback(job_id: str) -> bool:
    """Mark a claimed result callback as fully processed."""
    result = await DBProcessorJob.get_pymongo_collection().update_one(
        {
            "job_id": job_id,
            "result_callback_in_progress": True,
            "result_callback_processed": {"$ne": True},
        },
        {
            "$set": {
                "result_callback_processed": True,
                "result_callback_in_progress": False,
            }
        },
    )
    return result.modified_count == 1


# Workflow job operations

async def db_create_workflow_job(db_workflow_job: DBWorkflowJob) -> DBWorkflowJob:
    return await db_workflow_job.insert()


@call_sync
async def sync_db_create_workflow_job(db_workflow_job: DBWorkflowJob) -> DBWorkflowJob:
    return await db_create_workflow_job(db_workflow_job=db_workflow_job)


async def db_get_workflow_job(job_id: str) -> DBWorkflowJob:
    return await _get_document(
        DBWorkflowJob, DBWorkflowJob.job_id == job_id,
        f'Workflow job with id "{job_id}" not in the DB.',
    )


@call_sync
async def sync_db_get_workflow_job(job_id: str) -> DBWorkflowJob:
    return await db_get_workflow_job(job_id)


# Workflow script operations

async def db_create_workflow_script(db_workflow_script: DBWorkflowScript) -> DBWorkflowScript:
    return await db_workflow_script.insert()


@call_sync
async def sync_db_create_workflow_script(db_workflow_script: DBWorkflowScript) -> DBWorkflowScript:
    return await db_create_workflow_script(db_workflow_script=db_workflow_script)


async def db_get_workflow_script(workflow_id: str) -> DBWorkflowScript:
    return await _get_document(
        DBWorkflowScript, DBWorkflowScript.workflow_id == workflow_id,
        f'Workflow-script with id "{workflow_id}" not in the DB.',
    )


@call_sync
async def sync_db_get_workflow_script(workflow_id: str) -> DBWorkflowScript:
    return await db_get_workflow_script(workflow_id)


async def db_find_first_workflow_script_by_content(content_hash: str) -> DBWorkflowScript:
    return await _get_document(
        DBWorkflowScript, DBWorkflowScript.content_hash == content_hash,
        f'Workflow-script with content_hash "{content_hash}" not in the DB.',
    )


@call_sync
async def sync_db_find_first_workflow_script_by_content(content_hash: str) -> DBWorkflowScript:
    return await db_find_first_workflow_script_by_content(content_hash)


# Database validation

def verify_database_uri(mongodb_address: str) -> str:
    try:
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