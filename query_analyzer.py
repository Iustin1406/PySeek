from mixed_text_analyzer import MixedTextAnalyzer


class QueryAnalyzer:
    """
    Processes a search query into lexical tokens used for full-text search
    """

    def __init__(self):
        self.mixed_text_analyzer = MixedTextAnalyzer()

    def analyze(self, query):
        if not query:
            return []

        tokens = self.mixed_text_analyzer.analyze(query)

        # remove duplicates
        tokens = list(dict.fromkeys(tokens))

        return tokens