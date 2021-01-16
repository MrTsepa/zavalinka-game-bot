import logging

import requests
import urllib

from .WiktionaryHtmlParser import WiktionaryHtmlParser


class WiktionarySearcher(object):
    url = 'https://ru.wiktionary.org/wiki/'

    def __init__(self):
        self.parser = WiktionaryHtmlParser()
        self.logger = logging.getLogger(__name__)

    def search(self, word):
        encoded_word = urllib.parse.quote_plus(word)
        r = requests.get(WiktionarySearcher.url + encoded_word)
        if r.status_code == requests.codes.not_found:
            self.logger.warning(f'Coudn\'t find meaning for word {word}')
            return
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
            return
        return self.parser.parse(r.text)

    def generate_word(self):
        url = WiktionarySearcher.url + urllib.parse.quote_plus('Служебная:RandomInCategory/Русский_язык')
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
            return
        return self.parser.parse(r.text)

