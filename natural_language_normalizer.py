from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


class NaturalLanguageNormalizer:
    """
    Normalizes English words for lexical search,
     for example some stopped words may be removed (ex: that)
     and also use Snowball stemming
     moreover we keep the original matching form
     example:
     executes -> [executes,execut]
    """

    def __init__(self):
        self.stop_words = set(
            stopwords.words("english")
        )

        self.stemmer = SnowballStemmer(
            "english"
        )

    def normalize(self, word, remove_stop_words=True):
        if not word:
            return []

        word = word.lower()

        if remove_stop_words and word in self.stop_words:
            return []

        tokens = [word]

        stem = self.stemmer.stem(word)

        if stem != word:
            tokens.append(stem)

        return tokens