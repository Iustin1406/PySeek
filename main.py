from search_engine import SearchEngine


def main():
    repository_path = "."
    query = "where do we retry failed HTTP requests?"

    search_engine = SearchEngine()
    results = search_engine.search(repository_path, query)

    for result in results:
        print(result["function_name"])
        print(result["score"])
        print(result["function_filepath"])
        print()


if __name__ == "__main__":
    main()