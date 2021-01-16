import pandas as pd
from wordfreq import zipf_frequency, word_frequency

from wordlist.src.WiktionarySearcher import WiktionarySearcher

if __name__ == '__main__':
    wordlist = pd.read_csv('./wordlist_sample.tsv', encoding='utf8', sep='\t')

    wiki = WiktionarySearcher()
    for word in wordlist.word.values:
        print(wiki.search(word))
        print('{} - {} | {}'.format(word,
                                    zipf_frequency(word, 'ru', wordlist='large'),
                                    word_frequency(word, 'ru', wordlist='large')))

    for i in range(5):
        word, meanings = wiki.generate_word()
        freq = zipf_frequency(word, 'ru')
        print(f'{word} - {freq}: {meanings}')
