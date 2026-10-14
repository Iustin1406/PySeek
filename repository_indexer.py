import os

from database import Database
from embedder import Embedder
from repository_parser import RepositoryParser


# This class prepares the repo and saves its parsed units in the database
class RepositoryIndexer:
    def index_repository(self, repository_path):
        repository_path = os.path.abspath(repository_path)

        repository_parser = RepositoryParser()
        functions = repository_parser.parse_repository(repository_path)

        embedder = Embedder()
        embedded_functions = embedder.embed_functions(functions)

        database = Database()
        database.replace_repository_functions(
            repository_path,
            functions,
            embedded_functions
        )
        database.close()