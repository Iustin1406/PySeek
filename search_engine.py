from database import Database
from embedder import Embedder


class SearchEngine:
    def search(self, query):
        query = query.strip()
        if query == "":
            raise ValueError("Empty query")

        embedder = Embedder()
        query_embedding = embedder.embed_query(query)[0]

        database = Database()
        results = database.search(query_embedding)

        processed_results = self.format_results(results)
        database.close()

        return processed_results

    def format_results(self,db_rows):
        results = []
        for row in db_rows:
            results.append(
                {
                    "function_name": row[0],
                    "filepath": row[1],
                    "scope": row[2],
                    "score": row[3]
                }
            )

        return results