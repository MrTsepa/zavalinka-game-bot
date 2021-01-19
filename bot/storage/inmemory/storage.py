from dataclasses import dataclass, field
import typing

from bot.dto.room import Room


@dataclass
class Storage:
    rooms: typing.Dict[Room.ID_TYPE, Room] = field(default_factory=dict)
