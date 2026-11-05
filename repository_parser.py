import os

from python_code_parser import PythonCodeParser


class RepositoryParser:

    def __init__(self):
        self.python_parser = PythonCodeParser()
        self.functions = []
        self.python_files = []

        self.ignored_directories = [".git", ".venv", "venv", "__pycache__", "node_modules"]

    def parse_repository(self, repository_path):
        self.functions = []

        python_files = self.find_python_files(
            repository_path
        )

        for filepath in python_files:
            try:
                functions_from_file = self.python_parser.parse_file(
                    filepath
                )

                self.functions.extend(functions_from_file)

            except (SyntaxError, OSError, UnicodeDecodeError):
                print("Could not parse:", filepath)

        return self.functions

    def find_python_files(self, repository_path):
        self.python_files = []

        if not os.path.exists(repository_path):
            raise FileNotFoundError("Path does not exist")

        if not os.path.isdir(repository_path):
            raise NotADirectoryError("Path is not a directory")

        self._find_python_files(
            repository_path
        )

        return self.python_files

    def _find_python_files(self, directory_path):
        for element_name in os.listdir(directory_path):
            element_path = os.path.join(
                directory_path,
                element_name
            )

            if os.path.isdir(element_path):
                if element_name in self.ignored_directories:
                    continue

                self._find_python_files(
                    element_path
                )

            elif os.path.isfile(element_path):
                if element_name.endswith(".py"):
                    self.python_files.append(
                        element_path
                    )

    def parse_file(self, filepath):
        return self.python_parser.parse_file(
            filepath
        )