from collections import defaultdict
from dataclasses import dataclass, field
import typing

from bot.dto.user import User


@dataclass
class Scoreboard:
    scores: typing.Dict[User, int] = field(default_factory=lambda: defaultdict(int))
