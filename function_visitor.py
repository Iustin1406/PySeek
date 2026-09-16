import ast

from function_unit import FunctionUnit
from scope import Scope, ScopeType


class FunctionVisitor(ast.NodeVisitor):

    def __init__(self, source_code, filepath):
        self.source_code = source_code
        self.filepath = filepath

        self.functions = []
        self.scope_stack = []

    def visit_ClassDef(self, node):
        scope = Scope(node.name, ScopeType.CLASS)
        self.scope_stack.append(scope)

        self.generic_visit(node)

        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_function(node)

    def _visit_function(self, node):
        class_name = None
        parent_function_name = None

        if len(self.scope_stack) > 0:
            parent_scope = self.scope_stack[-1]

            if parent_scope.scope_type == ScopeType.CLASS:
                class_name = parent_scope.name

            if parent_scope.scope_type == ScopeType.FUNCTION:
                parent_function_name = parent_scope.name

        scope_path = []

        for scope in self.scope_stack:
            scope_path.append(scope.name)

        scope_path.append(node.name)

        function_unit = FunctionUnit(
            name=node.name,
            class_name=class_name,
            parent_function_name=parent_function_name,
            filepath=self.filepath,
            start_line=node.lineno,
            end_line=node.end_lineno,
            docstring=ast.get_docstring(node),
            source_code=ast.get_source_segment(
                self.source_code,
                node
            ),
            scope_path=scope_path
        )

        self.functions.append(function_unit)

        function_scope = Scope(
            node.name,
            ScopeType.FUNCTION
        )

        self.scope_stack.append(function_scope)

        self.generic_visit(node)

        self.scope_stack.pop()