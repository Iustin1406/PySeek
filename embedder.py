from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed_functions(self, functions):
        texts = []

        for function in functions:
            text = function.to_embedding_text()
            texts.append(text)

        embeddings = self.model.encode(texts)

        return embeddings

    def embed_query(self, query):
        embedding = self.model.encode([query])

        return embedding