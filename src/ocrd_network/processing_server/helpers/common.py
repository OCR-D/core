from fastapi import HTTPException
from logging import Logger
from typing import Optional


def raise_http_exception(logger: Logger, status_code: int, message: str, error: Optional[Exception] = None) -> None:
    if error:
        message = f"{message} {error}"
    logger.exception(message)
    raise HTTPException(status_code=status_code, detail=message)
