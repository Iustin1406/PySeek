from repository_parser import RepositoryParser
from embedder import Embedder

class SearchEngine:
    def search(self,repository_path, query):

        repository_parser = RepositoryParser()

        functions = repository_parser.parse_repository(repository_path)

        embedder = Embedder()

        function_embeddings = embedder.embed_functions(functions)

        query_embedding = embedder.embed_query(query)

        similarities = embedder.model.similarity(
            query_embedding,
            function_embeddings
        )

        scores = similarities[0]

        sorted_indexes = sorted(
            range(len(scores)),
            key=lambda index: scores[index].item(),
            reverse=True
        )

        results=[]

        for index in sorted_indexes[:5]:
            function = functions[index]
            score = scores[index].item()

            result={
                "score":score,
                "function_name":function.name,
                "function_filepath":function.filepath,
                "function_scope":function.scope_path,
            }

            results.append(result)

        return results
