import sys

from repository_indexer import RepositoryIndexer
from search_engine import SearchEngine


def main():
    command = sys.argv[1]

    if command == "index":
        repository_path = sys.argv[2]

        indexer = RepositoryIndexer()
        indexer.index_repository(repository_path)

        print("Repository indexed")

    elif command == "search":
        query = sys.argv[2]

        search_engine = SearchEngine()
        results = search_engine.search(query)

        for result in results:
            print(result)


if __name__ == "__main__":
    main()