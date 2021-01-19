from dataclasses import dataclass, field
import typing


@dataclass
class GameState:
    question_idx: int
    user_descriptions: typing.Dict[int, str] = field(default_factory=dict)
    poll_description_order: typing.List[typing.Tuple[str, typing.Optional[int]]] = field(default_factory=list)
    user_votes: typing.Dict[int, int] = field(default_factory=dict)
    user_question_message_id: typing.Dict[int, int] = field(default_factory=dict)
    poll_id: str = None
    poll_message_id: int = None
