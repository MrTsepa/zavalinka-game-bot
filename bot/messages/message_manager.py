import logging
import os

import pandas as pd


class MessageManager(object):
    def __init__(self, send_func, lang='en'):
        messages_file = f'./messages_{lang}.tsv'
        assert os.path.isfile(messages_file), f'Messages for language {lang} do not exist'
        self.messages = pd.read_csv(messages_file, encoding='utf8', sep='\t', index_col=0)
        self.send_func = send_func
        self.logger = logging.getLogger(__name__)

    def __send(self, message, **send_kwargs):
        self.logger.info(message)
        self.send_func(message, **send_kwargs)

    def greeting(self, **send_kwargs):
        message = self.messages.loc['START'].text
        self.__send(message, **send_kwargs)

    def user_added_ok(self, **send_kwargs):
        message = self.messages.loc['ADD_ME_SUCCESS'].text
        self.__send(message, **send_kwargs)

    def user_added_dubbed(self, **send_kwargs):
        message = self.messages.loc['ADD_ME_DUB'].text
        self.__send(message, **send_kwargs)

    def unknown_user(self, **send_kwargs):
        message = self.messages.loc['UNKNOWN_USER'].text
        self.__send(message, **send_kwargs)

    def start_game(self):
        messages = [self.messages.loc[f'GAME_START_{idx}'].text for idx in range(1, 4)]

    def start_round(self, **kwargs):
        message = self.messages.loc[f'ROUND_START_1'].text.format(kwargs.pop('word'))
        self.__send(message, **kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    message_manager = MessageManager(print)
    message_manager.greeting()
    message_manager.user_added_ok()
    message_manager.start_round(word='word')
