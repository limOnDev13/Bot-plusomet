"""The module responsible for processing the results of moderation."""

from typing import List
from logging import getLogger

from aiogram import Bot
from aiogram.types.reaction_type_emoji import ReactionTypeEmoji

from producer_consumer.moderation_results.base import BaseModerationResultConsumer
from schemas.messages import ModerationResultSchema
from bot.config.bot_config import BotConfig

from .reactions import REACTION

logger = getLogger("bot.services")


class PostModerationManager(object):
    """The class responsible for processing the moderation results."""

    def __init__(
        self,
        bot: Bot,
        config: BotConfig,
        mod_res_consumer: BaseModerationResultConsumer,
    ):
        """
        Init class.

        :param bot: Aiogram bot object.
        :param config: Config for bot.
        :param mod_res_consumer: Moderation result Consumer.
        """
        self.__bot = bot
        self.__chat_id = config.chat_id
        self.__is_premium = config.is_premium
        self.__mod_res_consumer = mod_res_consumer

    def __get_reaction_depending_on_moderation(
        self,
        mod_result: ModerationResultSchema,
    ) -> List[ReactionTypeEmoji]:
        """
        Return the reaction depending on the moderation.

        :param mod_result: Moderation result.

        :return: Reaction.
        """
        reactions: List[ReactionTypeEmoji] = list()

        if self.__is_premium:
            if mod_result.generated_by_llm:
                logger.debug("Message is generated.")
                reactions.append(REACTION["generated_by_llm"])
            if mod_result.toxic:
                logger.debug("Message is toxic.")
                reactions.append(REACTION["toxic"])
        else:
            if mod_result.generated_by_llm:
                logger.debug("Message is generated.")
                reactions = [REACTION["generated_by_llm"]]
            if mod_result.toxic:
                logger.debug("Message is toxic.")
                reactions = [REACTION["toxic"]]

        return reactions

    async def __set_reaction(
        self,
        mod_result: ModerationResultSchema,
    ) -> None:
        """Set reaction depends on moderation result."""
        reactions: List[ReactionTypeEmoji] = self.__get_reaction_depending_on_moderation(mod_result)
        if reactions:
            await self.__bot.set_message_reaction(
                chat_id=self.__chat_id,
                message_id=int(mod_result.msg_id),
                reaction=self.__get_reaction_depending_on_moderation(mod_result),
            )
        else:
            logger.debug("No reactions.")

    async def run(self):
        """
        Run post-moderation process.

        The function extracts the moderation results from the queue in an infinite loop,
        and depending on these results, sets a reaction to the message.
        :return: None.
        """
        while True:
            # extract
            logger.debug("Extract moderation result.")
            moderation_result: ModerationResultSchema = (
                await self.__mod_res_consumer.extract()
            )

            # process
            await self.__set_reaction(moderation_result)
