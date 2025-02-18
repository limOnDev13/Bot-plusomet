"""The module responsible for testing the module llm_moderator.py."""

import warnings
from typing import List

from server.schemas.messages import MessageSchema, ModerationResultSchema
from server.services.moderators.llm_moderator import LLMModerator


def test_moderation_user_msgs(
    llm_moderator: LLMModerator, user_msgs: List[MessageSchema]
) -> None:
    """Test class LLMModerator and method moderate on user msgs."""
    for msg in user_msgs:
        result: ModerationResultSchema = llm_moderator.moderate(msg)
        if result.generated_by_llm is not False:
            warnings.warn(
                f"LLM considers the message generated, "
                f"it was expected that it would identify "
                f"it as written by a real person. Msg:\n{msg.text}"
            )
        if result.toxic is not False:
            warnings.warn(
                f"LLM considers the message is toxic, "
                f"it was expected that it would identify "
                f"it as not toxic. Msg:\n{msg.text}"
            )


def test_moderation_generated_msgs(
    llm_moderator: LLMModerator, llm_generated_msgs: List[MessageSchema]
) -> None:
    """Test class LLMModerator and method moderate on generated msgs."""
    for msg in llm_generated_msgs:
        result = llm_moderator.moderate(msg)
        if result.generated_by_llm is not True:
            warnings.warn(
                f"LLM considers the message to be written by a real person,"
                f" it was expected that it would identify it as generated."
                f" Msg: {msg.text}"
            )


def test_moderation_toxic_msgs(
    llm_moderator: LLMModerator, toxic_msgs: List[MessageSchema]
) -> None:
    """Test class LLMModerator and method moderate on toxic msgs."""
    for msg in toxic_msgs:
        result = llm_moderator.moderate(msg)
        if result.toxic is not True:
            warnings.warn(
                f"LLM considers the message is not toxic, "
                f"it was expected that it would identify "
                f"it as toxic. Msg:\n{msg.text}"
            )
