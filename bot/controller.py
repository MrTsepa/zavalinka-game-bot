from bot.data.storage import Storage
from bot.data.room import Room
from bot.data.user import User


class StorageController:
    def __init__(self):
        self.storage = Storage()

    def create_room(self, room_id: Room.ID_TYPE) -> None:
        pass

    def add_user_to_room(self, room_id: Room.ID_TYPE, user: User) -> None:
        pass

    def start_game(self, room_id: Room.ID_TYPE) -> None:
        pass
