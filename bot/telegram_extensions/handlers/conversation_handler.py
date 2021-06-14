from typing import Optional, Tuple, cast, Callable, Any, Dict

from telegram import Update
from telegram.ext import ConversationHandler as TelegramConversationHandler, \
    CallbackContext, Dispatcher, DispatcherHandlerStop
from telegram.ext.conversationhandler import CheckUpdateType, _ConversationTimeoutContext
from telegram.utils.types import HandlerArg

from bot.telegram_extensions.conversation_context import ConversationContext


class ConversationHandler(TelegramConversationHandler):
    def __init__(
            self,
            state_entry_callbacks: Dict[object, Callable[[Update, CallbackContext], None]] = None,
            state_reentry_callback: Dict[object, Callable[[Update, CallbackContext], None]] = None,
            *args,
            **kwargs
    ):
        super(ConversationHandler, self).__init__(*args, **kwargs)
        self.state_entry_callbacks = state_entry_callbacks or {}
        self.state_reentry_callback = state_reentry_callback or {}

    def collect_additional_context(
        self,
        context: CallbackContext,
        update: HandlerArg,
        dispatcher: Dispatcher,
        check_result: CheckUpdateType,
    ) -> None:
        super(ConversationHandler, self).collect_additional_context(context, update, dispatcher, check_result)
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
        """Copied from super method to run `collect_additional_context` and call `update_state` with more arguments
        """
        if context:
            self.collect_additional_context(context, update, dispatcher, check_result)

        update = cast(Update, update)  # for mypy
        conversation_key, handler, check_result = check_result
        raise_dp_handler_stop = False

        with self._timeout_jobs_lock:
            # Remove the old timeout job (if present)
            timeout_job = self.timeout_jobs.pop(conversation_key, None)

            if timeout_job is not None:
                timeout_job.schedule_removal()
        try:
            new_state = handler.handle_update(update, dispatcher, check_result, context)
        except DispatcherHandlerStop as exception:
            new_state = exception.state
            raise_dp_handler_stop = True
        with self._timeout_jobs_lock:
            if self.conversation_timeout and new_state != self.END and dispatcher.job_queue:
                # Add the new timeout job
                self.timeout_jobs[conversation_key] = dispatcher.job_queue.run_once(
                    self._trigger_timeout,
                    self.conversation_timeout,
                    context=_ConversationTimeoutContext(
                        conversation_key, update, dispatcher, context
                    ),
                )

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self.update_state(self.END, conversation_key, update, context)
            if raise_dp_handler_stop:
                raise DispatcherHandlerStop(self.map_to_parent.get(new_state))
            return self.map_to_parent.get(new_state)

        self.update_state(new_state, conversation_key, update, context)
        if raise_dp_handler_stop:
            # Don't pass the new state here. If we're in a nested conversation, the parent is
            # expecting None as return value.
            raise DispatcherHandlerStop()
        return None

    def update_state(
            self,
            new_state: object,
            key: Tuple[int, ...],
            update: HandlerArg,
            context: CallbackContext,
    ) -> None:
        old_state = context.bot_data['conversation_context'].old_state
        if new_state is not None:
            if new_state in self.state_entry_callbacks and new_state != old_state:
                self.state_entry_callbacks[new_state](update, context)
            elif new_state in self.state_reentry_callback:
                self.state_reentry_callback[new_state](update, context)
        super(ConversationHandler, self).update_state(new_state, key)
