from logging import Logger
from pathlib import Path
from typing import List, Optional

from fastapi import status
from ocrd.resolver import Resolver
from ocrd.workspace import Workspace

from ...database import db_create_workspace, db_get_workspace
from ...models import DBWorkspace, PYJobInput
from .common import raise_http_exception


async def create_workspace_if_not_exists(logger: Logger, mets_path: str) -> DBWorkspace:
    try:
        # Core cannot create workspaces by API, but the Processing Server needs
        # the workspace in the database. The workspace is created if the path is
        # available locally and not existing in the database - since it has not
        # been uploaded through the Workspace Server.
        return await db_create_workspace(mets_path)
    except FileNotFoundError as error:
        message = f"Mets file path not existing: {mets_path}"
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


async def get_from_database_workspace(
    logger: Logger,
    workspace_id: Optional[str] = None,
    workspace_mets_path: Optional[str] = None
) -> DBWorkspace:
    try:
        return await db_get_workspace(workspace_id, workspace_mets_path)
    except ValueError as error:
        message = f"Workspace with id '{workspace_id}' not found in the DB."
        raise_http_exception(logger, status.HTTP_404_NOT_FOUND, message, error)


async def validate_and_return_mets_path(logger: Logger, job_input: PYJobInput) -> str:
    if job_input.workspace_id:
        db_workspace = await get_from_database_workspace(logger, job_input.workspace_id)
        return db_workspace.workspace_mets_path
    return job_input.path_to_mets


def validate_first_task_input_file_groups_existence(
    logger: Logger, mets_path: str, input_file_grps: List[str]
) -> None:
    # Validate the input file groups of the first task in the workflow.
    available_groups = Workspace(Resolver(), Path(mets_path).parents[0]).mets.file_groups
    for group in input_file_grps:
        if group not in available_groups:
            message = f"Input file group '{group}' of the first processor not found: {input_file_grps}"
            raise_http_exception(logger, status.HTTP_422_UNPROCESSABLE_ENTITY, message)