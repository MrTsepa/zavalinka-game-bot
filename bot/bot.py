from enum import Enum, auto
import random
import pathlib
from typing import Optional

from telegram import Update, ForceReply, Message as TelegramMessage
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, PollAnswerHandler

from bot.telegram_extensions.handlers.conversation_handler import ConversationHandler
from bot.telegram_extensions.conversation_context import ConversationContext

from bot.storage.inmemory.controller import InmemoryStorageController
from bot.messages.message_reader import MessageReader
from bot.messages.message import Message

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

    def __init__(self, token, assets_path: pathlib.Path):
        self.token = token
        self.storage_controller = InmemoryStorageController()
        self.message_reader = MessageReader(assets_path)

        self.words_per_game = 4

    def __send(self, message: Message, context: CallbackContext, update: Update,
               reply: bool = True, chat_id: Optional[int] = None, format_kwargs: Optional[dict] = None,
               send_message_kwargs: Optional[dict] = None) -> TelegramMessage:
        if format_kwargs is None:
            format_kwargs = {}
        if send_message_kwargs is None:
            send_message_kwargs = {}
        message = self.message_reader[message].format(**format_kwargs)
        if chat_id is not None:
            return context.bot.send_message(chat_id, message, **send_message_kwargs)
        if reply:
            return update.message.reply_text(message, **send_message_kwargs)
        return context.bot.send_message(update.effective_chat.id, message, **send_message_kwargs)

    def start_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        self.storage_controller.create_room(room_id)
        self.__send(Message.START, context, update)
        return Bot.State.INIT_STATE

    def add_me_command(self, update: Update, context: CallbackContext) -> Optional[State]:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.storage_controller.is_user_in_room(room_id, update.effective_user.id):
            self.storage_controller.add_user_to_room(room_id, update.effective_user)
            self.__send(Message.ADD_ME_SUCCESS, context, update)
        else:
            self.__send(Message.ADD_ME_DUB, context, update)
        return None

    def remove_me_command(self, update: Update, context: CallbackContext) -> Optional[State]:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.storage_controller.is_user_in_room(room_id, update.effective_user.id):
            self.__send(Message.REMOVE_ME_FAIL, context, update)
            return None

        self.storage_controller.remove_user_from_room(room_id, update.effective_user)
        self.__send(Message.REMOVE_ME_SUCCESS, context, update)

        conversation_context: Optional[ConversationContext] = context.bot_data.get('conversation_context', None)
        if conversation_context and conversation_context.old_state == Bot.State.INIT_STATE:
            return None

        if not self.storage_controller.get_users_in_room(room_id):
            self.__send(Message.GAME_END_EVERYBODY_LEFT, context, update)
            return ConversationHandler.END
        return None

    def start_game_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.storage_controller.is_user_in_room(room_id, update.effective_user.id):
            self.__send(Message.UNKNOWN_USER, context, update)
            return Bot.State.INIT_STATE
        self.__send(Message.GAME_START_1, context, update)
        self.storage_controller.start_game(room_id, generate_wordlist(self.words_per_game))
        self.__send(Message.GAME_START_2, context, update, reply=False)
        return Bot.State.WAIT_ANS

    def vote_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        if not self.storage_controller.get_current_user_descriptions(room_id):
            self.__send(Message.NO_VERSIONS, context, update)
            return Bot.State.WAIT_ANS

        description_order = [(self.storage_controller.get_current_description(room_id), None)]
        description_order.extend((
            (description, user_id)
            for user_id, description in self.storage_controller.get_current_user_descriptions(room_id).items()
        ))
        assert len(description_order) > 1

        random.shuffle(description_order)
        self.storage_controller.set_poll_description_order(room_id, description_order)

        sent_message = update.message.reply_poll(
            f'{self.storage_controller.get_current_word(room_id)}',
            [description[:100] for description, user in description_order],
            is_anonymous=False,
        )
        self.storage_controller.add_poll(room_id, sent_message.poll.id, sent_message.message_id)
        return Bot.State.WAIT_VOTE

    def vote_poll_answer(self, update: Update, context: CallbackContext):
        room_id = self.storage_controller.get_room_id_by_poll_id(update.poll_answer.poll_id)
        chat_id = room_id_to_chat_id(room_id)
        if room_id is None:
            return
        self.storage_controller.add_user_vote(room_id, update.poll_answer.user.id, update.poll_answer.option_ids[0])

        if len(self.storage_controller.get_user_votes(room_id)) == len(self.storage_controller.get_users_in_room(room_id)):
            context.bot.stop_poll(
                chat_id, self.storage_controller.get_poll_message_id(room_id)
            )
            self.__send(Message.VOTE_SUCCESS, context, update, chat_id=chat_id)

    def results_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        user_dict = self.storage_controller.get_users_in_room(room_id)
        results = {user_id: 0 for user_id in user_dict}
        results['official'] = 0
        description_order = self.storage_controller.get_description_order(room_id)
        for user_id, vote in self.storage_controller.get_user_votes(room_id).items():
            author_id = description_order[vote][1]
            if author_id is None:
                results['official'] += 1
            else:
                results[author_id] += 1
        result_string = '\n'.join(
            f'{user_dict[user_id].username if user_id != "official" else user_id}: {result}'
            for user_id, result in results.items()
        )
        self.__send(Message.ROUND_END_1, context, update, format_kwargs={'results': result_string})
        self.__send(Message.ROUND_END_2, context, update, chat_id=room_id_to_chat_id(room_id))
        return Bot.State.ROUND_FINISH

    def next_command(self, update: Update, context: CallbackContext) -> State:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        try:
            self.storage_controller.next_round(room_id)
        except IndexError:
            self.__send(Message.QUESTIONS_ENDED, context, update)
            return Bot.State.INIT_STATE
        return Bot.State.WAIT_ANS

    def stop_game_command(self, update: Update, context: CallbackContext) -> int:
        self.__send(Message.GAME_END, context, update)
        return ConversationHandler.END

    def receive_description_from_user(self, update: Update, context: CallbackContext) -> None:
        if not update.message.reply_to_message:
            self.__send(Message.PRIVATE_NEED_REPLY, context, update, chat_id=update.effective_user.id)
            return
        room_id = self.storage_controller.get_room_id_by_private_message_id(
            update.effective_user.id,
            update.message.reply_to_message.message_id,
        )
        self.storage_controller.add_user_description(
            room_id,
            update.effective_user.id,
            update.message.text
        )
        self.__send(Message.ANSWER_SAVED, context, update)

        if len(self.storage_controller.get_users_in_room(room_id)) == \
                len(self.storage_controller.get_current_user_descriptions(room_id)):
            chat_id = room_id_to_chat_id(room_id)
            self.__send(Message.VOTE_READY, context, update, chat_id=chat_id)

    def end_state_entry(self, update: Update, context: CallbackContext) -> None:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        self.storage_controller.remove_room(room_id)

    def wait_ans_entry(self, update: Update, context: CallbackContext) -> None:
        room_id = chat_id_to_room_id(update.effective_chat.id)
        word = self.storage_controller.get_current_word(room_id)
        self.__send(Message.ROUND_START_1, context, update, reply=False, format_kwargs={'word': word})
        self.__send(Message.ROUND_START_2, context, update, reply=False)
        for user_id in self.storage_controller.get_users_in_room(room_id):
            sent_message = self.__send(
                Message.ROUND_START_1, context, update,
                chat_id=user_id, format_kwargs={'word': word}, send_message_kwargs={'reply_markup': ForceReply()}
            )
            self.storage_controller.add_user_question_message_id(room_id, user_id, sent_message.message_id)

    def start(self):
        updater = Updater(self.token, use_context=True)

        dispatcher = updater.dispatcher
        dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                Bot.State.INIT_STATE: [
                    CommandHandler("start_game", self.start_game_command),
                    CommandHandler("add_me", self.add_me_command),
                    CommandHandler("remove_me", self.remove_me_command),
                ],
                Bot.State.WAIT_ANS: [
                    CommandHandler("vote", self.vote_command),
                    CommandHandler("add_me", self.add_me_command),
                    CommandHandler("remove_me", self.remove_me_command),
                ],
                Bot.State.WAIT_VOTE: [
                    CommandHandler("results", self.results_command),
                    CommandHandler("add_me", self.add_me_command),
                    CommandHandler("remove_me", self.remove_me_command),
                ],
                Bot.State.ROUND_FINISH: [
                    CommandHandler("next", self.next_command),
                    CommandHandler("add_me", self.add_me_command),
                    CommandHandler("remove_me", self.remove_me_command),
                ],
            },
            state_entry_callbacks={
                ConversationHandler.END: self.end_state_entry,
                Bot.State.WAIT_ANS: self.wait_ans_entry,
            },
            fallbacks=[CommandHandler("stop_game", self.stop_game_command)],
            per_chat=True,
            per_user=False,
            per_message=False,
            allow_reentry=True,
        ))
        dispatcher.add_handler(PollAnswerHandler(self.vote_poll_answer))
        dispatcher.add_handler(MessageHandler(Filters.chat_type.private, self.receive_description_from_user))

        updater.start_polling()

        updater.idle()
