from dataclasses import dataclass, field

from bot.dto.question_set import QuestionSet
from bot.dto.scoreboard import Scoreboard


@dataclass
class Game:
    question_set: QuestionSet
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
