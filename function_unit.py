from embeddable import Embeddable


class FunctionUnit(Embeddable):
    def __init__(
            self,
            name,
            filepath,
            start_line,
            end_line,
            source_code,
            class_name=None,
            parent_function_name=None,
            docstring=None,
            #list of enclosing scope names for a specific AST node
            scope_path=None
    ):
        self.name = name
        self.class_name = class_name
        self.parent_function_name = parent_function_name
        self.filepath = filepath
        self.start_line = start_line
        self.end_line = end_line
        self.docstring = docstring
        self.source_code = source_code
        self.scope_path = scope_path

    def to_embedding_text(self):
        parts = [
            self.name,
            self.class_name,
            self.parent_function_name,
            self.docstring,
            self.source_code
        ]

        return "\n".join(part for part in parts if part)