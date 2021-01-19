from dataclasses import dataclass

from bot.dto.question_set import QuestionSet


@dataclass
class Game:
    question_set: QuestionSet
