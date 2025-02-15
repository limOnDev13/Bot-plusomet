"""The module responsible for the endpoints related to moderation."""

import logging

from fastapi import APIRouter

from server.schemas.moderation_schemas import ModerationIn, ModerationOut

logger = logging.getLogger("main_logger.router")

router: APIRouter = APIRouter(tags=["moderation"])


@router.post("/api/moderate", status_code=200, response_model=ModerationOut)
async def moderate_msg(user_msg: ModerationIn):
    """Moderate the message."""
    pass
