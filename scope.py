from enum import Enum


class ScopeType(Enum):
    CLASS = "class"
    FUNCTION = "function"

# used to parse the code and know the context type for an ast node
class Scope:
    def __init__(self, name, scope_type):
        self.name = name
        self.scope_type = scope_type