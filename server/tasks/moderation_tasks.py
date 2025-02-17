"""The module responsible for Celery moderation tasks."""

from logging import getLogger
from typing import Callable

from celery.exceptions import MaxRetriesExceededError

from server.celery_app import app
from server.schemas.messages import MessageSchema, ModerationResultSchema
from server.services.excs import APIAuthException, TooManyRequests
from server.services.moderators.llm_moderator import LLMModerator

logger = getLogger("main.celery")


class ModerationManager(object):
    """
    The class responsible for the queue of messages for moderation.

    The class is a single interface for message moderation.
    The class is based on Celery. A message is sent to the class object,
    and the moderation of this message is added to the queue.
    If moderation works without errors, the processing of the moderation result
    is added to another queue. The class is abstracted from
    the implementation of post-moderation,
    its implementation is left to the responsibility of the developer.
    It is enough for the developer to pass the post-moderation function
    as an argument when initializing the class.
    The class itself will wrap the function in a Celery task.
    """

    def __init__(
        self,
        moderator: LLMModerator,
        post_moderation_func: Callable[[ModerationResultSchema], None],
        moderation_queue_name: str = "moderation",
        post_moderation_queue_name: str = "processing",
    ):
        """
        Init class.

        :param moderator: LLMModerator object
        :param post_moderation_func: post-moderation function.
        :type post_moderation_func: Callable[[ModerationResultSchema], None]
        :param moderation_queue_name: The name of the queue where
        the moderation tasks are stored.
        :param post_moderation_queue_name: The name of the queue where
        the post-moderation tasks are stored.
        """
        self.__moderator = moderator
        self.__post_moderation_task = self.__create_post_moderation_task(
            post_moderation_func
        )
        self.__moderation_queue_name = moderation_queue_name
        self.__post_moderation_queue_name = post_moderation_queue_name

    @classmethod
    def __create_post_moderation_task(
        cls, post_moderation_func: Callable[[ModerationResultSchema], None]
    ):
        """Return Celery task from post-moderation func."""
        return app.task()(post_moderation_func)

    @app.task(
        bind=True,
        autoretry_for=(APIAuthException, TooManyRequests),
        max_retries=5,
        retry_backoff=True,
    )
    def __moderate_msg_task(
        self,
        task_self,  # from bind=True
        msg: MessageSchema,
    ) -> None:
        """Moderate message and add post-moderation into queue."""
        try:
            # Get moderation result
            moderation_result: ModerationResultSchema = self.__moderator.moderate(msg)
            # Add processing moderation result in queue
            self.__post_moderation_task.apply_async(
                args=(moderation_result,), queue=self.__post_moderation_queue_name
            )
        except APIAuthException as exc:
            logger.warning(
                "Authorization error on the %s service." " Trying to auth again...",
                exc.service_name,
            )
            self.__moderator.llm_api.auth()  # auth again
            try:
                raise task_self.retry(exc=exc, max_retries=3, countdown=10)
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
                raise task_self.retry(exc=exc)
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

    def moderate_msg(self, msg: MessageSchema):
        """Add moderation message into queue."""
        self.__moderate_msg_task.apply_async(
            args=(msg,), queue=self.__moderation_queue_name
        )
