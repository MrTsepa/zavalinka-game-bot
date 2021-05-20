import random
from typing import List, Tuple

from wordfreq import zipf_frequency

from wordlist.RuWiktionary import RuWiktionary


def format_description(description: str) -> str:
    if len(description) <= 0:
        return description
    return description[:1].upper() + description[1:]


def generate_wordlist(n: int) -> List[Tuple[str, str]]:
    wiki = RuWiktionary()
    words = []
    while len(words) < n:
        try:
            word = wiki.generate_word()
        except Exception as e:
            continue
        text, meanings = word.text, word.meanings
        if word.is_proper_noun():
            continue
        if not meanings:
            continue
        freq = zipf_frequency(text, 'ru')
        if freq > 1:
            continue
        words.append((text, random.choice(meanings)))
    return words
