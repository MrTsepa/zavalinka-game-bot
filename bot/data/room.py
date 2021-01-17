from dataclasses import dataclass, field
import typing

from bot.data.game import Game
from bot.data.game_state import GameState
from bot.data.user import User


@dataclass
class Room:
    ID_TYPE = str

    id: ID_TYPE
    game: Game = None
    game_state: GameState = None
    participants: typing.List[User] = field(default_factory=list)
