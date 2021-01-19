from enum import Enum, auto
import random

from telegram import Update, Chat
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler, PollAnswerHandler

from bot.controller import StorageController
from bot.messages.message_reader import MessageReader, Messages

from wordlist import generate_wordlist


def chat_id_to_room_id(chat_id: int) -> str:
    return str(chat_id)


def room_id_to_chat_id(room_id: str) -> int:
    return int(room_id)


class Bot:
    class State(Enum):
        INIT_STATE = auto()
        WAIT_ANS = auto()
        WAIT_VOTE = auto()
        ROUND_FINISH = auto()

    def __init__(self, token):
        self.token = token
        self.controller = StorageController()
        self.message_reader = MessageReader()

        self.words_per_game = 1

    def __send(self, message, context, update, reply=True, chat_id=None, message_kwargs={}):
        message = self.message_reader[message].format(**message_kwargs)
        if chat_id is not None:
            return context.bot.send_message(chat_id, message)
        if reply:
            return update.message.reply_text(message)
        return context.bot.send_message(update.effective_chat.id, message)

    def start_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        self.controller.create_room(room_id)
        self.__send(Messages.START, context, update)
        return Bot.State.INIT_STATE

    def add_me_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.controller.is_user_in_room(room_id, update.effective_user.id):
            self.controller.add_user_to_room(room_id, update.effective_user)
            self.__send(Messages.ADD_ME_SUCCESS, context, update)
        else:
            self.__send(Messages.ADD_ME_DUB, context, update)
        return Bot.State.INIT_STATE

    def start_game_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.controller.is_user_in_room(room_id, update.effective_user.id):
            self.__send(Messages.UNKNOWN_USER, context, update)
            return Bot.State.INIT_STATE
        self.__send(Messages.GAME_START_1, context, update)
        self.controller.start_game(room_id, generate_wordlist(self.words_per_game))
        self.__send(Messages.GAME_START_2, context, update, reply=False)
        word = self.controller.get_current_word(room_id)
        self.__send(Messages.ROUND_START_1, context, update, reply=False, message_kwargs={'word': word})
        self.__send(Messages.ROUND_START_2, context, update, reply=False)
        for user_id in self.controller.get_users_in_room(room_id):
            sent_message = self.__send(Messages.ROUND_START_1, context, update, chat_id=user_id, message_kwargs={'word': word})
            self.controller.add_user_question_message_id(room_id, user_id, sent_message.message_id)
        return Bot.State.WAIT_ANS

    def vote_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.controller.get_current_user_descriptions(room_id):
            self.__send(Messages.NO_VERSIONS, context, update)
            return Bot.State.WAIT_ANS

        description_order = [(self.controller.get_current_description(room_id), None)]
        description_order.extend((
            (description, user_id)
            for user_id, description in self.controller.get_current_user_descriptions(room_id).items()
        ))
        assert len(description_order) > 1

        random.shuffle(description_order)
        self.controller.set_poll_description_order(room_id, description_order)

        sent_message = update.message.reply_poll(
            f'{self.controller.get_current_word(room_id)}',
            [description[:100] for description, user in description_order],
            is_anonymous=False,
        )
        self.controller.add_poll(room_id, sent_message.poll.id, sent_message.message_id)
        return Bot.State.WAIT_VOTE

    def vote_poll_answer(self, update: Update, context: CallbackContext):
        room_id = self.controller.get_room_id_by_poll_id(update.poll_answer.poll_id)
        chat_id = room_id_to_chat_id(room_id)
        if room_id is None:
            return
        self.controller.add_user_vote(room_id, update.poll_answer.user.id, update.poll_answer.option_ids[0])

        if len(self.controller.get_user_votes(room_id)) == len(self.controller.get_users_in_room(room_id)):
            context.bot.stop_poll(
                chat_id, self.controller.get_poll_message_id(room_id)
            )
            self.__send(Messages.VOTE_SUCCESS, context, update, chat_id=chat_id)

    def results_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        user_dict = self.controller.get_users_in_room(room_id)
        results = {user_id: 0 for user_id in user_dict}
        results['official'] = 0
        description_order = self.controller.get_description_order(room_id)
        for user_id, vote in self.controller.get_user_votes(room_id).items():
            author_id = description_order[vote][1]
            if author_id is None:
                results['official'] += 1
            else:
                results[author_id] += 1
        result_string = '\n'.join(
            f'{user_dict[user_id].username if user_id != "official" else user_id}: {result}'
            for user_id, result in results.items()
        )
        self.__send(Messages.ROUND_END_1, context, update, message_kwargs={'results': result_string})
        self.__send(Messages.ROUND_END_2, context, update, chat_id=room_id_to_chat_id(room_id))
        return Bot.State.ROUND_FINISH

    def next_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        try:
            self.controller.next_round(room_id)
        except IndexError:
            self.__send(Messages.QUESTIONS_ENDED, context, update)
            return Bot.State.INIT_STATE
        word = self.controller.get_current_word(room_id)
        self.__send(Messages.ROUND_START_1, context, update, message_kwargs={'word': word})
        self.__send(Messages.ROUND_START_2, context, update, reply=False)
        for user_id in self.controller.get_users_in_room(room_id):
            sent_message = self.__send(Messages.ROUND_START_1, context, update, chat_id=user_id, message_kwargs={'word': word})
            self.controller.add_user_question_message_id(room_id, user_id, sent_message.message_id)
        return Bot.State.WAIT_ANS

    def stop_game_command(self, update: Update, context: CallbackContext) -> int:
        self.__send(Messages.GAME_END, context, update)
        return ConversationHandler.END

    def receive_description_from_user(self, update: Update, context: CallbackContext) -> None:
        if update.effective_chat.type != Chat.PRIVATE:
            return
        room_id = self.controller.get_room_id_by_private_message_id(
            update.effective_user.id,
            update.message.reply_to_message.message_id,
        )
        self.controller.add_user_description(
            room_id,
            update.effective_user.id,
            update.message.text
        )
        self.__send(Messages.ANSWER_SAVED, context, update)

        if len(self.controller.get_users_in_room(room_id)) == \
                len(self.controller.get_current_user_descriptions(room_id)):
            chat_id = room_id_to_chat_id(room_id)
            self.__send(Messages.VOTE_READY, context, update, chat_id=chat_id)

    def start(self):
        updater = Updater(self.token, use_context=True)

        dispatcher = updater.dispatcher
        dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                Bot.State.INIT_STATE: [
                    CommandHandler("add_me", self.add_me_command),
                    CommandHandler("start_game", self.start_game_command)
                ],
                Bot.State.WAIT_ANS: [CommandHandler("vote", self.vote_command)],
                Bot.State.WAIT_VOTE: [CommandHandler("results", self.results_command)],
                Bot.State.ROUND_FINISH: [CommandHandler("next", self.next_command)],
            },
            fallbacks=[CommandHandler("stop_game", self.stop_game_command)],
            per_chat=True,
            per_user=False,
            per_message=False,
            allow_reentry=True,
        ))
        dispatcher.add_handler(PollAnswerHandler(self.vote_poll_answer))
        dispatcher.add_handler(MessageHandler(Filters.reply, self.receive_description_from_user))

        updater.start_polling()

        updater.idle()
