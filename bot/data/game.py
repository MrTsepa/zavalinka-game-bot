from dataclasses import dataclass

from bot.data.question_set import QuestionSet


@dataclass
class Game:
    question_set: QuestionSet
