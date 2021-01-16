from enum import Enum
import string

import bs4


class Word(object):
    class POS(Enum):
        Noun = 1
        Adj = 2
        Verb = 3
        Other = 4

    def __init__(self, text=None, grammar=None, meanings=None):
        self.text = text
        self.grammar = grammar
        self.meanings = meanings

    def get_pos(self):
        if 'существительное' in self.grammar:
            return Word.POS.Noun
        elif 'прилагательное' in self.grammar:
            return Word.POS.Adj
        elif 'глагол' in self.grammar:
            return Word.POS.Verb
        else:
            return Word.POS.Other


class WiktionaryHtmlParser(object):
    def __init__(self, shortcuts=None):
        self.shortcuts = self.__parse_shortcuts(shortcuts)

    def parse(self, html_doc):
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        word = soup.find('h1', id='firstHeading').get_text()
        grammar = self.__fetch_grammar(soup)
        meanings = self.__fetch_meanings(soup)
        return Word(word, grammar, meanings)

    def __fetch_grammar(self, soup):
        morphology = soup.find(id='Морфологические_и_синтаксические_свойства')
        grammar = morphology.get_text() #.find_next('p').find_next('p')
        return grammar

    def __fetch_meanings(self, soup):
        semantics = soup.find(id='Семантические_свойства')
        meanings = self.__parse_list(semantics.find_next('ol'))
        return meanings

    def __parse_shortcuts(self, html_doc):
        if html_doc is None:
            return dict()
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        items = soup.find_all('li')
        shortcuts = {}
        for item in items:
            if ' — ' not in item:
                continue
            shortcut, meaning = item.get_text().split(' — ')[:2]
            shortcut, meaning = shortcut.strip(), meaning.strip()
            shortcuts[shortcut] = meaning
        return shortcuts

    def __parse_list(self, list_elem):
        result = []
        for li in list_elem.find_all('li'):
            item = []
            for tok in li:
                tok = self.__normalize(tok)
                if tok is None:
                    continue
                if tok in {',', ';'}:
                    if len(item) == 0:
                        continue
                    tok = item[-1] + tok
                    item.pop(-1)
                item.append(tok)
            if len(item) == 0:
                continue
            result.append(' '.join(item))
        return result

    def __normalize(self, token):
        if token.name in {'span', 'sup'}:
            return None
        if not isinstance(token, bs4.NavigableString):
            token = token.get_text()
        token = token.strip()
        if len(token) == 0:
            return None
        if token in self.shortcuts:
            return None
        return token
