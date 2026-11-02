import re


class IdentifierTokenizer:
    """
    Converts code identifiers in smaller tokens used for lexical processing

    For example HTTPResponseParser returns
    ["HTTPResponseParser", "http", "response", "parser"]
    """
    def tokenize(self, identifier):
        if not identifier:
            return []

        tokens = [identifier]

        # first we split snake_case identifiers
        snake_parts = identifier.split("_")

        for part in snake_parts:
            if not part:
                continue

            camel_parts = self._split_camel_case(part)

            for camel_part in camel_parts:
                token = camel_part.lower()

                if token not in tokens:
                    tokens.append(token)

        #return only the lowercase word if we don't get other components from its tokenization
        if len(tokens)==2 and tokens[0].lower()==tokens[1]:
            return [tokens[1]]

        return tokens

    def _split_camel_case(self, text):
        return re.findall(
            r"[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+",
            text
        )