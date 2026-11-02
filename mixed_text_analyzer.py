import re

from identifier_tokenizer import IdentifierTokenizer
from natural_language_normalizer import NaturalLanguageNormalizer


class MixedTextAnalyzer:
    """
    Analyzes text that may contain both natural language and code identifiers.
    """

    def __init__(self):
        self.identifier_tokenizer = IdentifierTokenizer()
        self.natural_language_normalizer = NaturalLanguageNormalizer()

    def analyze(self, text):
        if not text:
            return []

        tokens = []

        words = re.findall(r"[A-Za-z0-9_]+", text)

        for word in words:
            identifier_tokens = self.identifier_tokenizer.tokenize(word)

            # if the word was decomposed into multiple parts, it may be a code identifier
            if len(identifier_tokens) > 1:
                analyzed_tokens = self._analyze_identifier(
                    word,
                    identifier_tokens
                )

            # if not, it's probably natural language
            else:
                analyzed_tokens = (
                    self.natural_language_normalizer.normalize(
                        word,
                        remove_stop_words=True
                    )
                )

            tokens.extend(analyzed_tokens)

        return tokens

    def _analyze_identifier(
            self,
            identifier,
            identifier_tokens
    ):
        tokens = []

        for token in identifier_tokens:

            if token not in tokens:
                tokens.append(token)


            if token == identifier and len(identifier_tokens) > 1:
                continue

            normalized_tokens = (
                self.natural_language_normalizer.normalize(
                    token,
                    remove_stop_words=False
                )
            )

            for normalized_token in normalized_tokens:
                if normalized_token not in tokens:
                    tokens.append(normalized_token)

        return tokens