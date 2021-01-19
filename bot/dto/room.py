from dataclasses import dataclass, field
import typing

from bot.dto.game import Game
from bot.dto.game_state import GameState
from bot.dto.user import User


@dataclass
class Room:
    ID_TYPE = str

    id: ID_TYPE
    game: Game = None
    game_state: GameState = None
    participants: typing.Dict[int, User] = field(default_factory=dict)
