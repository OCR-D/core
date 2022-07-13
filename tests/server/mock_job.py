from ocrd.server.models.job import Job


class MockJob(Job):

    async def insert(self, *, link_rule=None, session=None, skip_actions=None):
        pass
