import ast

from function_visitor import FunctionVisitor


class PythonCodeParser:

    def parse_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            source_code = file.read()

        tree = ast.parse(source_code)

        visitor = FunctionVisitor(source_code, filepath)
        visitor.visit(tree)

        return visitor.functions