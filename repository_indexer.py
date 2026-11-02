import os

from code_text_analyzer import CodeTextAnalyzer
from database import Database
from embedder import Embedder
from repository_parser import RepositoryParser


# This class prepares the repo and saves its parsed units in the database
class RepositoryIndexer:
    def index_repository(self, repository_path):
        repository_path = os.path.abspath(repository_path)

        repository_parser = RepositoryParser()
        functions = repository_parser.parse_repository(repository_path)

        #semantic representation
        embedder = Embedder()
        embedded_functions = embedder.embed_functions(functions)

        #lexical representation
        code_text_analyzer = CodeTextAnalyzer()
        analyzed_functions = []

        for function in functions:
            analyzed_function = code_text_analyzer.analyze(function)
            analyzed_functions.append(analyzed_function)

        database = Database()
        database.replace_repository_functions(
            repository_path,
            functions,
            embedded_functions,
            analyzed_functions
        )
        database.close()