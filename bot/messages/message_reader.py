from enum import Enum, auto
import logging
import os

import pandas as pd


class Messages(Enum):
    START = auto()
    ADD_ME_SUCCESS = auto()
    ADD_ME_DUB = auto()
    UNKNOWN_USER = auto()
    GAME_START_1 = auto()
    GAME_START_2 = auto()
    ROUND_START_1 = auto()
    ROUND_START_2 = auto()
    NO_VERSIONS = auto()
    ANSWER_SAVED = auto()
    VOTE_READY = auto()
    VOTE_SUCCESS = auto()
    ROUND_END_1 = auto()
    ROUND_END_2 = auto()
    QUESTIONS_ENDED = auto()
    PRIVATE_NEED_REPLY = auto()
    GAME_END = auto()


class MessageReader(object):
    def __init__(self, lang='en'):
        import pathlib
        messages_file = f'{pathlib.Path(__file__).parent.absolute()}/messages_{lang}.tsv'
        assert os.path.isfile(messages_file), f'Messages for language {lang} do not exist'
        self.messages = pd.read_csv(messages_file, encoding='utf8', sep='\t', index_col=0)
        self.logger = logging.getLogger(__name__)

    def __getitem__(self, message):
        if message.name not in self.messages.index:
            self.logger.error(f'No such message {message}')
            return
        message = self.messages.loc[message.name].text
        self.logger.info(message)
        return message.replace('\\n', '\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    message_manager = MessageReader()
