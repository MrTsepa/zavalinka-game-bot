import random
from typing import List, Tuple

from wordfreq import zipf_frequency

from wordlist.WiktionarySearcher import WiktionarySearcher


def generate_wordlist(n: int) -> List[Tuple[str, str]]:
    wiki = WiktionarySearcher()
    words = []
    while len(words) < n:
        try:
            word = wiki.generate_word()
        except Exception as e:
            continue
        word, meanings = word.text, word.meanings
        if not meanings:
            continue
        freq = zipf_frequency(word, 'ru')
        if freq <= 1:
            words.append((word, random.choice(meanings)))
    return words
