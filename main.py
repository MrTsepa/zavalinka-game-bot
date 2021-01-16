import logging
import typing
from dataclasses import dataclass, field

import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

with open('.token', 'r') as f:
    TOKEN = f.readline()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


@dataclass
class Room:
    id: str
    admin: telegram.User
    participants: typing.List[telegram.User] = field(default_factory=list)


@dataclass
class Storage:
    rooms: typing.Dict[str, Room] = field(default_factory=dict)


storage = Storage()


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def create_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text(f'Please insert room id.')
        return
    room_id = context.args[0]

    if room_id in storage.rooms:
        if update.effective_user == storage.rooms[room_id].admin:
            update.message.reply_text(f'You are already an administrator of the room "{room_id}".')
            return
        update.message.reply_text(f'Room "{room_id}" is already administrated by another user.')

    storage.rooms[room_id] = Room(room_id, update.effective_user)
    update.message.reply_text(f'You have created room "{room_id}"!')


def join_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text(f'Please insert room id.')
        return
    room_id = context.args[0]

    if room_id not in storage.rooms:
        update.message.reply_text(f'Room with id "{room_id}" does not exist.')
        return

    room = storage.rooms[room_id]
    if update.effective_user == room.admin:
        update.message.reply_text(f'You are already an administrator of the room "{room_id}".')
        return

    if update.effective_user in room.participants:
        update.message.reply_text(f'You are already a participant of the room "{room_id}".')
        return

    room.participants.append(update.effective_user)
    update.message.reply_text(f'You are now a participant of the room "{room_id}".')


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("create", create_command))
    dispatcher.add_handler(CommandHandler("join", join_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
