from dataclasses import dataclass, field
import typing

from bot.dto.question import Question


@dataclass
class QuestionSet:
    questions: typing.List[Question] = field(default_factory=list)
