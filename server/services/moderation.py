"""The module responsible for the general logic of message moderation."""

from logging import getLogger

from producer_consumer.messages.base import BaseMessageConsumer
from producer_consumer.moderation_results.base import BaseModerationResultProducer
from schemas.messages import MessageSchema, ModerationResultSchema

from .excs import APIAuthException, APIException, PromptError, TooManyRequests
from .moderators.base import BaseModerator

logger = getLogger("main.moderation")


class ModerationManager(object):
    """The class responsible for moderation."""

    def __init__(
        self,
        msg_consumer: BaseMessageConsumer,
        mod_res_producer: BaseModerationResultProducer,
        moderator: BaseModerator,
    ):
        """
        Init class.

        :param msg_consumer: Message consumer. The message consumer
        must have a locking mechanism when the queue is empty.
        :param mod_res_producer: Moderation results producer.
        :param moderator: Moderator object.
        """
        self.__msg_consumer = msg_consumer
        self.__mod_res_producer = mod_res_producer
        self.__moderator = moderator

    async def run(self):
        """
        Start message moderation.

        The function takes messages out of the queue in an infinite loop,
        moderates them, and saves the result of moderation to another queue.
        :return: None
        """
        while True:
            # extract
            msg: MessageSchema = await self.__msg_consumer.extract()

            # moderate
            try:
                moderation_result: ModerationResultSchema = self.__moderator.moderate(
                    msg
                )
            except APIAuthException as exc:
                logger.error("Can't auth on %s.", exc.service_name)
            except TooManyRequests as exc:
                logger.error("Service %s is overloaded.", exc.service_name)
            except APIException as exc:
                logger.error(
                    "Unexpected error working with the %s API.\nexc: %s",
                    exc.service_name,
                    str(exc),
                )
            except PromptError as exc:
                logger.error("A logical error of the prompt.\nexc: %s", str(exc))
            except Exception as exc:
                logger.error("Unexpected error.\nexc: %s", str(exc))
            else:
                # upload
                await self.__mod_res_producer.upload(moderation_result)
