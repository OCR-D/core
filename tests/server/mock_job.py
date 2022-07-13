from typing import Optional, List, Union

from beanie import WriteRules
from beanie.odm.actions import ActionDirections
from beanie.odm.documents import DocType
from pymongo.client_session import ClientSession

from ocrd.server.models.job import Job


class MockJob(Job):

    async def insert(
            self: DocType,
            *,
            link_rule: WriteRules = WriteRules.DO_NOTHING,
            session: Optional[ClientSession] = None,
            skip_actions: Optional[List[Union[ActionDirections, str]]] = None,
    ):
        pass
