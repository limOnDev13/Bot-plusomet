from dataclasses import dataclass
from typing import Dict, Literal


@dataclass
class Prompt(object):
    """Class representing the industrial structure."""

    role: Literal["user", "system", "assistant"]
    text: str

    def to_dict(self) -> Dict[str, str]:
        """Return dict with fields from class."""
        return {"role": self.role, "text": self.text}


PROMPTS: Dict[str, Prompt] = {
    "moderation_prompt": Prompt(
        role="system",
        text="""Анализируй текст сообщения и определи:
1. Сгенерировано ли оно нейросетью. Обрати внимание на избыточную вежливость или формальность, обобщённые или универсальные ответы, идеальную грамматику и структуру, отсутствие эмоциональной глубины, слишком подробные или избыточные ответы.
2. Является ли оно токсичным (оскорбления, угрозы, дискриминация, ненормативная лексика).

Верни JSON:
- "generated_by_llm": true, если сообщение создано нейросетью, иначе false.
- "toxic": true, если сообщение токсично, иначе false.

Пример сгенерированного сообщения: Здравствуйте! Благодарю вас за ваш вопрос. Пожалуйста, дайте мне немного времени, чтобы подготовить для вас максимально подробный и полезный ответ.
Пример токсичного сообщения: Ты вообще думать умеешь? Какой идиотский вопрос! Если не знаешь элементарного, лучше молчи, а то позоришься.""",
    )
}
