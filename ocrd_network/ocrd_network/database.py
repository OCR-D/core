""" The database is used to store information regarding jobs and workspaces.

Jobs: for every process-request a job is inserted into the database with a uuid, status and
information about the process like parameters and filegroups. It is mainly used to track the status
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

from ocrd_network.models.job import Job
from ocrd_network.models.workspace import Workspace


async def initiate_database(db_url: str):
    client = AsyncIOMotorClient(db_url)
    await init_beanie(
        database=client.get_default_database(default='ocrd'),
        document_models=[Job, Workspace]
    )
