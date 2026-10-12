from database import Database
from embedder import Embedder
from repository_parser import RepositoryParser


#this class only prepares the repo and saves it's parsed units in the db
class RepositoryIndexer:
    def index_repository(self, repository_path):
        repository_parser = RepositoryParser()
        functions = repository_parser.parse_repository(repository_path)

        embedder = Embedder()
        embedded_functions = embedder.embed_functions(functions)

        database = Database()
        database.save_functions(functions, embedded_functions)
        database.close()