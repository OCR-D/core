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
