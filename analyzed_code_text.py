class AnalyzedCodeText:
    """
    Stores the lexical tokens extracted from a FunctionUnit in order to be processed for lexical search
    """

    def __init__(
            self,
            name_tokens,
            scope_tokens,
            docstring_tokens,
            identifier_tokens,
            comment_tokens,
            string_tokens
    ):
        self.name_tokens = name_tokens
        self.scope_tokens = scope_tokens
        self.docstring_tokens = docstring_tokens
        self.identifier_tokens = identifier_tokens
        self.comment_tokens = comment_tokens
        self.string_tokens = string_tokens