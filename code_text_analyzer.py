import ast
import io
import keyword
import tokenize

from analyzed_code_text import AnalyzedCodeText
from identifier_tokenizer import IdentifierTokenizer
from mixed_text_analyzer import MixedTextAnalyzer
from natural_language_normalizer import NaturalLanguageNormalizer


class CodeTextAnalyzer:
    """
    Extracts and processes lexical info from a FunctionUnit.
    """

    def __init__(self):
        self.identifier_tokenizer = IdentifierTokenizer()
        self.mixed_text_analyzer = MixedTextAnalyzer()
        self.natural_language_normalizer = NaturalLanguageNormalizer()

    def analyze(self, function):
        name_tokens = self._analyze_identifier(
            function.name
        )

        scope_tokens = self._analyze_scope(
            function.scope_path,
            function.name
        )

        docstring_tokens = self.mixed_text_analyzer.analyze(
            function.docstring
        )

        (
            identifier_tokens,
            comment_tokens,
            string_tokens
        ) = self._analyze_source_code(
            function.source_code,
            function.docstring
        )

        return AnalyzedCodeText(
            name_tokens=name_tokens,
            scope_tokens=scope_tokens,
            docstring_tokens=docstring_tokens,
            identifier_tokens=identifier_tokens,
            comment_tokens=comment_tokens,
            string_tokens=string_tokens
        )

    def _analyze_identifier(self, identifier):
        if not identifier:
            return []

        identifier_tokens = (
            self.identifier_tokenizer.tokenize(
                identifier
            )
        )

        tokens = []

        for token in identifier_tokens:
            if token not in tokens:
                tokens.append(token)

            # Keep the complete compound identifier unchanged.
            #
            # Example:
            # restore_connection
            #
            # Stemming is applied only to its components.
            if (
                    token == identifier
                    and len(identifier_tokens) > 1
            ):
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

    def _analyze_scope(
            self,
            scope_path,
            function_name
    ):
        tokens = []

        if not scope_path:
            return tokens

        for scope_name in scope_path:

            # The current function is already represented
            # in lexical_name, so do not duplicate it here.
            if scope_name == function_name:
                continue

            scope_tokens = self._analyze_identifier(
                scope_name
            )

            tokens.extend(scope_tokens)

        return tokens

    def _analyze_source_code(
            self,
            source_code,
            docstring
    ):
        identifier_tokens = []
        comment_tokens = []
        string_tokens = []

        if not source_code:
            return (
                identifier_tokens,
                comment_tokens,
                string_tokens
            )

        source_reader = io.StringIO(
            source_code
        ).readline

        python_tokens = tokenize.generate_tokens(
            source_reader
        )

        docstring_skipped = False

        for token in python_tokens:

            if token.type == tokenize.NAME:
                self._process_name_token(
                    token.string,
                    identifier_tokens
                )

            elif token.type == tokenize.COMMENT:
                self._process_comment_token(
                    token.string,
                    comment_tokens
                )

            elif token.type == tokenize.STRING:
                string_value = self._get_string_value(
                    token.string
                )

                # The docstring has already been processed
                # separately.
                if (
                        docstring
                        and not docstring_skipped
                        and string_value == docstring
                ):
                    docstring_skipped = True
                    continue

                self._process_string_token(
                    string_value,
                    string_tokens
                )

        return (
            identifier_tokens,
            comment_tokens,
            string_tokens
        )

    def _process_name_token(
            self,
            text,
            tokens
    ):
        # Skip Python keywords such as:
        # def, return, if, for, etc.
        if keyword.iskeyword(text):
            return

        analyzed_tokens = self._analyze_identifier(
            text
        )

        tokens.extend(analyzed_tokens)

    def _process_comment_token(
            self,
            text,
            tokens
    ):
        # Remove '#' before analyzing the comment.
        comment = text.lstrip("#").strip()

        comment_tokens = (
            self.mixed_text_analyzer.analyze(
                comment
            )
        )

        tokens.extend(comment_tokens)

    def _process_string_token(
            self,
            text,
            tokens
    ):
        if not text:
            return

        analyzed_tokens = (
            self.mixed_text_analyzer.analyze(
                text
            )
        )

        tokens.extend(analyzed_tokens)

    def _get_string_value(self, text):
        try:
            value = ast.literal_eval(text)

            if isinstance(value, str):
                return value

        except (ValueError, SyntaxError):
            pass

        return text