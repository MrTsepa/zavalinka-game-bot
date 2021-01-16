import logging
import typing
from dataclasses import dataclass, field
from more_itertools import ilen

import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from wordlist import generate_wordlist

with open('.token', 'r') as f:
    TOKEN = f.readline()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


@dataclass
class Question:
    word: str
    description: str


@dataclass
class QuestionSet:
    questions: typing.List[Question] = field(default_factory=list)


@dataclass
class Game:
    question_set: QuestionSet


@dataclass
class GameState:
    question_idx: int
    user_descriptions: typing.Dict[int, str] = field(default_factory=dict)
    user_votes: typing.Dict[int, int] = field(default_factory=dict)


@dataclass
class Room:
    id: str
    admin: telegram.User
    game: Game = None
    game_state: GameState = None
    participants: typing.List[telegram.User] = field(default_factory=list)

    @property
    def all_participants(self):
        return self.participants + [self.admin]


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
        return

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


def start_game_command(update: Update, context: CallbackContext) -> int:
    if not context.args:
        update.message.reply_text(f'Please insert room id.')
        return 0
    room_id = context.args[0]

    if room_id not in storage.rooms:
        update.message.reply_text(f'Room with id "{room_id}" does not exist.')
        return 0

    room = storage.rooms[room_id]

    if update.effective_user != room.admin:
        update.message.reply_text(f'You are not an administrator of the room "{room_id}".')
        return 0

    for user in room.all_participants:
        context.bot.send_message(user.id, 'Game is starting...')

    room.game = Game(QuestionSet(
        [Question(word, description) for word, description in generate_wordlist(5)]
    ))
    room.game_state = GameState(question_idx=0)
    context.bot.send_message(room.admin.id, f'Game is set up. To see first question type /next.')
    return 0


def answering_timer_ended(context: CallbackContext) -> None:
    room_id = str(context.job.context)
    room = storage.rooms[room_id]
    for user in room.all_participants:
        context.bot.send_message(user.id, 'Answering time ended.')
    correct_description = room.game.question_set.questions[room.game_state.question_idx].description
    descriptions = list(room.game_state.user_descriptions.values()) + [correct_description]
    reply_text = '\n'.join(f'{i + 1}. {description}' for i, description in enumerate(descriptions))
    for user in room.all_participants:
        context.bot.send_message(
            user.id,
            reply_text,
            reply_markup=ReplyKeyboardMarkup([list(range(1, len(descriptions) + 1))], one_time_keyboard=True)
        )
    context.job_queue.run_once(voting_timer_ended, 30, context=room_id, name=f'{room_id} voting')


def voting_timer_ended(context: CallbackContext) -> None:
    room_id = str(context.job.context)
    room = storage.rooms[room_id]
    for user in room.all_participants:
        context.bot.send_message(user.id, 'Voting time ended.')
    correct_description = room.game.question_set.questions[room.game_state.question_idx].description
    descriptions = list(room.game_state.user_descriptions.values()) + [correct_description]
    result = {}
    for i in range(len(descriptions)):
        result[i] = ilen(filter(lambda val: val == i, room.game_state.user_votes.values()))
    reply_text = '\n'.join(f'{i+1}: {votes}' for i, votes in result.items())
    for user in room.all_participants:
        context.bot.send_message(
            user.id,
            reply_text,
        )
    room.game_state = GameState(question_idx=room.game_state.question_idx + 1)
    context.bot.send_message(room.admin.id, f'To see next question type /next.')


def next_question_command(update: Update, context: CallbackContext) -> int:
    admin_rooms = list(filter(lambda room: update.effective_user == room.admin, storage.rooms.values()))
    if not admin_rooms:
        update.message.reply_text(f'You are not an admin of any room.')
        return 0
    if len(admin_rooms) > 1:
        update.message.reply_text(f'You are an admin of more than one room.')
        return 0
    admin_room = admin_rooms[0]

    if context.job_queue.get_jobs_by_name(f'{admin_room.id} answering') or \
            context.job_queue.get_jobs_by_name(f'{admin_room.id} voting'):
        update.message.reply_text(f'Wait until current word is finished.')
        return 0

    if admin_room.game_state.question_idx >= len(admin_room.game.question_set.questions):
        update.message.reply_text(f'You are out of questions.')
        return 0
    question = admin_room.game.question_set.questions[admin_room.game_state.question_idx]
    for user in admin_room.all_participants:
        context.bot.send_message(user.id, f'Next word: {question.word}')
    context.job_queue.run_once(answering_timer_ended, 30, context=admin_room.id, name=f'{admin_room.id} answering')


def receive_description_from_user(update: Update, context: CallbackContext) -> None:
    user_description = update.effective_message.text
    user_rooms = list(filter(lambda room: update.effective_user in room.all_participants, storage.rooms.values()))
    if not user_rooms:
        update.message.reply_text(f'You are not a participant of any room.')
        return
    if len(user_rooms) > 1:
        update.message.reply_text(f'You are a participant of more than one room.')
        return

    user_room = user_rooms[0]
    user_room.game_state.user_descriptions[update.effective_user.id] = user_description
    update.message.reply_text(f'Your description was saved.')


def receive_vote_from_user(update: Update, context: CallbackContext) -> None:
    user_vote = int(update.effective_message.text)
    user_rooms = list(filter(lambda room: update.effective_user in room.all_participants, storage.rooms.values()))
    if not user_rooms:
        update.message.reply_text(f'You are not a participant of any room.')
        return
    if len(user_rooms) > 1:
        update.message.reply_text(f'You are a participant of more than one room.')
        return

    user_room = user_rooms[0]
    user_room.game_state.user_votes[update.effective_user.id] = user_vote - 1
    update.message.reply_text(f'Your vote was saved.')


def stop_game_command(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Game is ended")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("create", create_command))
    dispatcher.add_handler(CommandHandler("join", join_command))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start_game", start_game_command)],
        states={
            0: [CommandHandler("next", next_question_command)]
        },
        fallbacks=[CommandHandler("stop_game", stop_game_command)]
    ))
    dispatcher.add_handler(MessageHandler(Filters.reply, receive_description_from_user))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(0|[1-9][0-9]*)$'), receive_vote_from_user))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
