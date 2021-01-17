import typing

from bot.data.storage import Storage
from bot.data.room import Room
from bot.data.user import User
from bot.data.game import Game
from bot.data.game_state import GameState
from bot.data.question_set import QuestionSet
from bot.data.question import Question


class StorageController:
    def __init__(self):
        self.storage = Storage()

    def create_room(self, room_id: Room.ID_TYPE) -> None:
        self.storage.rooms[room_id] = Room(room_id)

    def add_user_to_room(self, room_id: Room.ID_TYPE, user: User) -> None:
        self.storage.rooms[room_id].participants[user.id] = user

    def is_user_in_room(self, room_id: Room.ID_TYPE, user_id: int) -> bool:
        return user_id in self.storage.rooms[room_id].participants

    def get_users_in_room(self, room_id: Room.ID_TYPE) -> typing.Dict[int, User]:
        return self.storage.rooms[room_id].participants

    def start_game(self, room_id: Room.ID_TYPE, questions: typing.Iterable[typing.Tuple[str, str]]) -> None:
        self.storage.rooms[room_id].game = Game(QuestionSet(
            [Question(word, description) for word, description in questions]
        ))
        self.storage.rooms[room_id].game_state = GameState(0)

    def get_current_word(self, room_id: Room.ID_TYPE) -> str:
        room = self.storage.rooms[room_id]
        return room.game.question_set.questions[room.game_state.question_idx].word

    def get_current_description(self, room_id: Room.ID_TYPE) -> str:
        room = self.storage.rooms[room_id]
        return room.game.question_set.questions[room.game_state.question_idx].description

    def get_current_user_descriptions(self, room_id: Room.ID_TYPE) -> typing.Dict[int, str]:
        room = self.storage.rooms[room_id]
        return room.game_state.user_descriptions
