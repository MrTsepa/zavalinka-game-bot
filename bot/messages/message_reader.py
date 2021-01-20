import logging
import os
import pathlib

import pandas as pd

from bot.messages.message import Message


class MessageReader:
    def __init__(self, root_path: pathlib.Path, lang: str = 'en') -> None:
        messages_file = root_path / f'messages_{lang}.tsv'
        assert os.path.isfile(messages_file), f'Messages for language {lang} do not exist'
        self.messages = pd.read_csv(messages_file, encoding='utf8', sep='\t', index_col=0)
        self.logger = logging.getLogger(__name__)

    def __getitem__(self, message: Message) -> str:
        if message.name not in self.messages.index:
            self.logger.error(f'No such message {message}')
            raise LookupError
        message = self.messages.loc[message.name].text
        self.logger.info(message)
        return message.replace('\\n', '\n')
