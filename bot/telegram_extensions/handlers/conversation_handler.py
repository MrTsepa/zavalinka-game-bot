from typing import Optional

from telegram.ext import ConversationHandler as TelegramConversationHandler, CallbackContext, Dispatcher
from telegram.ext.conversationhandler import CheckUpdateType
from telegram.utils.types import HandlerArg

from bot.telegram_extensions.conversation_context import ConversationContext


class ConversationHandler(TelegramConversationHandler):
    def collect_additional_context(
        self,
        context: CallbackContext,
        update: HandlerArg,
        dispatcher: Dispatcher,
        check_result: CheckUpdateType,
    ) -> None:
        conversation_key, _, _ = check_result
        with self._conversations_lock:
            state = self.conversations.get(conversation_key)
        context.bot_data['conversation_context'] = ConversationContext(old_state=state, key=conversation_key)

    def handle_update(
            self,
            update: HandlerArg,
            dispatcher: Dispatcher,
            check_result: CheckUpdateType,
            context: CallbackContext = None,
    ) -> Optional[object]:
        if context:
            self.collect_additional_context(context, update, dispatcher, check_result)
        return super(ConversationHandler, self).handle_update(update, dispatcher, check_result, context)
