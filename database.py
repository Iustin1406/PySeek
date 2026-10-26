import psycopg
from pgvector.psycopg import register_vector


class Database:
    def __init__(self):
        self.connection = psycopg.connect("dbname=pyseek")
        register_vector(self.connection)

    #delete old functions from an already indexed repo and save the new version of it
    def replace_repository_functions(
            self,
            repository_path,
            functions,
            embeddings
    ):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM code_units
                WHERE repository_path = %s
                """,
                (repository_path,)
            )

            for function, embedding in zip(functions, embeddings):
                cursor.execute(
                    """
                    INSERT INTO code_units
                    (
                        repository_path,
                        name,
                        filepath,
                        start_line,
                        end_line,
                        scope_path,
                        source_code,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        repository_path,
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

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    def search(self, query_embedding, repository_path, limit=5):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT name, filepath, scope_path, start_line,
                   1 - (embedding <=> %s) AS score
            FROM code_units
            WHERE repository_path = %s
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                query_embedding,
                repository_path,
                query_embedding,
                limit
            )
        )

        results = cursor.fetchall()
        cursor.close()

        return results

    def close(self):
        self.connection.close()