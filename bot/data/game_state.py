from dataclasses import dataclass, field
import typing


@dataclass
class GameState:
    question_idx: int
    user_descriptions: typing.Dict[int, str] = field(default_factory=dict)
    user_votes: typing.Dict[int, int] = field(default_factory=dict)
