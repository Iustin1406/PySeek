import psycopg
from pgvector.psycopg import register_vector


class Database:
    def __init__(self):
        self.connection = psycopg.connect("dbname=pyseek")
        register_vector(self.connection)

    def save_function(self, function, embedding):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO code_units
            (name, filepath, start_line, end_line, scope_path, source_code, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                function.name,
                function.filepath,
                function.start_line,
                function.end_line,
                function.scope_path,
                function.source_code,
                embedding
            )
        )

        self.connection.commit()
        cursor.close()

    def save_functions(self, functions, embeddings):
        cursor = self.connection.cursor()

        for function, embedding in zip(functions, embeddings):
            cursor.execute(
                """
                INSERT INTO code_units
                (name, filepath, start_line, end_line, scope_path, source_code, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    function.name,
                    function.filepath,
                    function.start_line,
                    function.end_line,
                    function.scope_path,
                    function.source_code,
                    embedding
                )
            )

        self.connection.commit()
        cursor.close()

    def search(self, query_embedding, limit=5):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT name, filepath, scope_path,
                   1 - (embedding <=> %s) AS score
            FROM code_units
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                query_embedding,
                query_embedding,
                limit
            )
        )

        results = cursor.fetchall()
        cursor.close()

        return results

    def close(self):
        self.connection.close()