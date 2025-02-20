"""The module responsible for responding to messages."""

from typing import Dict

from aiogram.types.reaction_type_emoji import ReactionTypeEmoji

REACTION: Dict[str, ReactionTypeEmoji] = {
    "generated_by_llm": ReactionTypeEmoji(emoji="👾"),
    "toxic": ReactionTypeEmoji(emoji="🤮"),
}
