import typing

from bot.dto.room import Room
from bot.dto.user import User


class StorageControllerBase:
    def __init__(self):
        pass

    def create_room(self, room_id: Room.ID_TYPE) -> None:
        raise NotImplementedError()

    def add_user_to_room(self, room_id: Room.ID_TYPE, user: User) -> None:
        raise NotImplementedError()

    def is_user_in_room(self, room_id: Room.ID_TYPE, user_id: int) -> bool:
        raise NotImplementedError()

    def get_users_in_room(self, room_id: Room.ID_TYPE) -> typing.Dict[int, User]:
        raise NotImplementedError()

    def start_game(self, room_id: Room.ID_TYPE, questions: typing.Iterable[typing.Tuple[str, str]]) -> None:
        raise NotImplementedError()

    def next_round(self, room_id: Room.ID_TYPE) -> None:
        raise NotImplementedError()

    def get_current_word(self, room_id: Room.ID_TYPE) -> str:
        raise NotImplementedError()

    def get_current_description(self, room_id: Room.ID_TYPE) -> str:
        raise NotImplementedError()

    def get_current_user_descriptions(self, room_id: Room.ID_TYPE) -> typing.Dict[int, str]:
        raise NotImplementedError()

    def add_user_question_message_id(self, room_id: Room.ID_TYPE, user_id: int, message_id: int) -> None:
        raise NotImplementedError()

    def get_room_id_by_private_message_id(self, user_id: int, message_id: int) -> typing.Optional[Room.ID_TYPE]:
        raise NotImplementedError()

    def add_user_description(self, room_id: Room.ID_TYPE, user_id: int, description: str) -> None:
        raise NotImplementedError()

    def set_poll_description_order(self, room_id: Room.ID_TYPE,
                                   description_order: typing.List[typing.Tuple[str, typing.Optional[int]]]) -> None:
        raise NotImplementedError()

    def get_description_order(self, room_id: Room.ID_TYPE) -> typing.List[typing.Tuple[str, typing.Optional[int]]]:
        raise NotImplementedError()

    def add_poll(self, room_id: Room.ID_TYPE, poll_id: str, message_id: int) -> None:
        raise NotImplementedError()

    def get_room_id_by_poll_id(self, poll_id: str) -> typing.Optional[Room.ID_TYPE]:
        raise NotImplementedError()

    def get_poll_message_id(self, room_id) -> int:
        raise NotImplementedError()

    def add_user_vote(self, room_id: Room.ID_TYPE, user_id: int, vote: int) -> None:
        raise NotImplementedError()

    def get_user_votes(self, room_id: Room.ID_TYPE) -> typing.Dict[int, int]:
        raise NotImplementedError()
