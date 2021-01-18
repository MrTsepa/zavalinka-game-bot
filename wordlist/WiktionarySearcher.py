import logging
import random

import requests
import urllib

from wordlist.WiktionaryHtmlParser import WiktionaryHtmlParser


class WiktionarySearcher(object):
    url = 'https://ru.wiktionary.org/wiki/'

    def __init__(self):
        self.parser = WiktionaryHtmlParser(self.__fetch_shortcuts())
        self.logger = logging.getLogger(__name__)

    def search_meaning(self, word):
        encoded_word = urllib.parse.quote_plus(word)
        r = requests.get(WiktionarySearcher.url + encoded_word)
        if r.status_code == requests.codes.not_found:
            self.logger.warning(f'Coudn\'t find meaning for word {word}')
            return
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
            return
        return self.parser.parse(r.text).meanings

    def generate_word(self):
        pos = random.choice([
            'Русские_существительные',
            # 'Русские_прилагательные',
            # 'Русские_глаголы',
            # 'Русские_наречия',
        ])
        url = WiktionarySearcher.url + urllib.parse.quote_plus(f'Служебная:RandomInCategory/{pos}')
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
            return
        word = self.parser.parse(r.text)
        return word

    def __fetch_shortcuts(self):
        url = WiktionarySearcher.url + urllib.parse.quote_plus('Викисловарь:Условные_сокращения')
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
            return
        return r.text

