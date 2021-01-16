import bs4


class WiktionaryHtmlParser(object):
    def parse(self, html_doc):
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        word = soup.find('h1', id='firstHeading').get_text()
        semantics = soup.find(id='Семантические_свойства')
        meanings = self.__parse_list(semantics.find_next('ol'))
        return word, meanings

    def __parse_list(self, list_elem):
        result = []
        for li in list_elem.find_all('li'):
            item = []
            for tok in li:
                tok = self.__normalize(tok)
                if tok is None:
                    continue
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
        return token
