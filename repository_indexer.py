import hashlib
import os

from code_text_analyzer import CodeTextAnalyzer
from database import Database
from embedder import Embedder
from repository_parser import RepositoryParser


CURRENT_INDEX_VERSION = 1


# This class prepares the repo and saves its parsed units in the database
class RepositoryIndexer:
    def index_repository(self, repository_path):
        repository_path = os.path.abspath(repository_path)

        repository_parser = RepositoryParser()
        python_files = repository_parser.find_python_files(
            repository_path
        )

        database = Database()

        try:
            indexed_rows = database.get_indexed_files(
                repository_path
            )

            indexed_files = {}

            for row in indexed_rows:
                indexed_files[row[1]] = {
                    "id": row[0],
                    "hash": row[2],
                    "version": row[3]
                }

            seen_files = set()

            embedder = None
            code_text_analyzer = CodeTextAnalyzer()

            for filepath in python_files:
                relative_filepath = os.path.relpath(
                    filepath,
                    repository_path
                )

                seen_files.add(relative_filepath)

                content_hash = self._calculate_file_hash(
                    filepath
                )

                indexed_file = indexed_files.get(
                    relative_filepath
                )

                if not self._should_reindex(
                        indexed_file,
                        content_hash
                ):
                    print("UNCHANGED:", relative_filepath)
                    continue

                if indexed_file is None:
                    print("NEW:", relative_filepath)
                else:
                    print("MODIFIED:", relative_filepath)

                try:
                    functions = repository_parser.parse_file(
                        filepath
                    )

                except (SyntaxError, OSError, UnicodeDecodeError):
                    print("Could not parse:", filepath)
                    continue

                #semantic representation
                if functions:
                    if embedder is None:
                        embedder = Embedder()

                    embedded_functions = (
                        embedder.embed_functions(
                            functions
                        )
                    )
                else:
                    embedded_functions = []

                #lexical representation
                analyzed_functions = []

                for function in functions:
                    analyzed_function = (
                        code_text_analyzer.analyze(
                            function
                        )
                    )

                    analyzed_functions.append(
                        analyzed_function
                    )

                database.replace_indexed_file(
                    repository_path,
                    relative_filepath,
                    content_hash,
                    CURRENT_INDEX_VERSION,
                    functions,
                    embedded_functions,
                    analyzed_functions
                )

            indexed_paths = set(
                indexed_files.keys()
            )

            deleted_files = (
                    indexed_paths - seen_files
            )

            for filepath in deleted_files:
                print("DELETED:", filepath)

                indexed_file_id = indexed_files[filepath]["id"]

                database.delete_indexed_file(
                    indexed_file_id
                )

        finally:
            database.close()

    def _should_reindex(
            self,
            indexed_file,
            content_hash
    ):
        if indexed_file is None:
            return True

        if (
                indexed_file["version"]
                != CURRENT_INDEX_VERSION
        ):
            return True

        if (
                indexed_file["hash"]
                != content_hash
        ):
            return True

        return False

    def _calculate_file_hash(self, filepath):
        sha256 = hashlib.sha256()

        with open(filepath, "rb") as file:
            while True:
                chunk = file.read(8192)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()