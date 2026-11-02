import os

from database import Database
from embedder import Embedder
from query_analyzer import QueryAnalyzer

class SearchEngine:

    def search(self, query, repository_path):
        query = query.strip()

        if query == "":
            raise ValueError("Empty query")

        repository_path = os.path.abspath(repository_path)

        embedder = Embedder()
        query_embedding = embedder.embed_query(query)[0]

        database = Database()

        semantic_rows = database.semantic_search(
            query_embedding,
            repository_path,
            limit=10
        )

        query_analyzer = QueryAnalyzer()
        query_tokens = query_analyzer.analyze(query)

        lexical_rows = database.lexical_search(
            query_tokens,
            repository_path,
            limit=10
        )

        database.close()

        semantic_results = self.format_results(semantic_rows)
        lexical_results = self.format_results(lexical_rows)

        results = self.reciprocal_rank_fusion(
            semantic_results,
            lexical_results
        )

        return results[:5]

    def format_results(self, db_rows):
        results = []

        for row in db_rows:
            results.append(
                {
                    "function_name": row[0],
                    "filepath": row[1],
                    "scope": row[2],
                    "start_line": row[3],
                    "score": row[4]
                }
            )

        return results

    def reciprocal_rank_fusion(
            self,
            semantic_results,
            lexical_results,
            k=60
    ):
        # combines semantic and lexical search results by rewarding functions that rank highly in both lists
        combined_results = {}

        rankings = [
            semantic_results,
            lexical_results
        ]

        for ranking in rankings:
            for rank, result in enumerate(ranking, start=1):

                key = (
                    result["filepath"],
                    result["start_line"]
                )

                if key not in combined_results:
                    combined_results[key] = {
                        "function_name": result["function_name"],
                        "filepath": result["filepath"],
                        "scope": result["scope"],
                        "start_line": result["start_line"],
                        "score": 0
                    }

                combined_results[key]["score"] += 1 / (k + rank)

        results = list(combined_results.values())

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results