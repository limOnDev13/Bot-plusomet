"""The module responsible for Celery moderation tasks."""

from logging import getLogger
from typing import Callable

from celery.exceptions import MaxRetriesExceededError

from server.celery_app import app
from server.schemas.messages import MessageSchema, ModerationResultSchema
from server.services.excs import APIAuthException, TooManyRequests
from server.services.moderators.llm_moderator import LLMModerator

logger = getLogger("main.celery")


@app.task(
    queue="moderation",
    bind=True,
    autoretry_for=(APIAuthException, TooManyRequests),
    max_retries=5,
    retry_backoff=True,
)
def moderate_msg(
    self, msg: MessageSchema, moderator: LLMModerator
) -> ModerationResultSchema:
    try:
        return moderator.moderate(msg)
    except APIAuthException as exc:
        logger.warning(
            "Authorization error on the %s service." " Trying to auth again...",
            exc.service_name,
        )
        moderator.llm_api.auth()  # auth again
        try:
            raise self.retry(exc=exc, max_retries=3, countdown=10)
        except MaxRetriesExceededError:
            logger.error(
                "The maximum number of authorization attempts has been reached."
            )
            raise
    except TooManyRequests as exc:
        logger.warning(
            "There are too many requests to the %s service."
            " Trying to make a request again...",
            exc.service_name,
        )
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error(
                "The maximum number of attempts to make"
                " a request to the %s service has been reached.",
                exc.service_name,
            )
            raise
    except Exception as exc:
        logger.error(str(exc))
        raise
