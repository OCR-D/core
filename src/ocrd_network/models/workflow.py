from beanie import Document


class DBWorkflowScript(Document):
    """ Model to store a workflow-script in the database
    """
    workflow_id: str
    content: str
    content_hash: str
