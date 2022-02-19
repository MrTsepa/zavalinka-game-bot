import random
from typing import List, Tuple

import pandas as pd
import numpy as np

from wordfreq import zipf_frequency

from wordlist.WiktionarySearcher import WiktionarySearcher


def generate_wordlist(n: int, mode='wiki', **kwargs) -> List[Tuple[str, str]]:
    if mode == 'wiki':
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
    elif mode == 'curated':
        df = pd.read_csv(kwargs['assets_path'] / 'curated_wordlist.tsv', sep='\t')
        return random.sample(df[np.logical_not(pd.isna(df.description))].values.tolist(), n)
