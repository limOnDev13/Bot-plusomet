"""The module responsible for testing the module llm_moderator.py."""

from typing import List

from server.services.moderators.llm_moderator import LLMModerator, ModerationResult


def test_llm_moderator(
    llm_moderator: LLMModerator,
    user_msgs: List[str],
    llm_generated_msgs: List[str],
    toxic_msgs: List[str],
) -> None:
    """Test class LLMModerator and method moderate."""
    for msg in user_msgs:
        result: ModerationResult = llm_moderator.moderate(msg)
        print(msg)
        assert result.generated_by_llm is False
        assert result.toxic is False

    for msg in llm_generated_msgs:
        result = llm_moderator.moderate(msg)
        print(msg)
        assert result.generated_by_llm is True

    for msg in toxic_msgs:
        result = llm_moderator.moderate(msg)
        print(msg)
        assert result.toxic is True
