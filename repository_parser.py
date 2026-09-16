import os

from python_code_parser import PythonCodeParser


class RepositoryParser:

    def __init__(self):
        self.python_parser = PythonCodeParser()
        self.functions = []

        self.ignored_directories = [".git", ".venv", "venv", "__pycache__"]

    def parse_repository(self, repository_path):
        self.functions = []

        self._parse_directory(repository_path)

        return self.functions

    def _parse_directory(self, directory_path):
        for element_name in os.listdir(directory_path):
            element_path = os.path.join(directory_path, element_name)

            if os.path.isdir(element_path):
                if element_name in self.ignored_directories:
                    continue

                self._parse_directory(element_path)

            elif os.path.isfile(element_path):
                if element_name.endswith(".py"):
                    functions_from_file = self.python_parser.parse_file(
                        element_path
                    )

                    self.functions.extend(functions_from_file)