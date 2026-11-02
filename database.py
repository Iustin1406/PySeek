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
            embeddings,
            analyzed_functions
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

            for function, embedding, analyzed_function in zip(
                    functions,
                    embeddings,
                    analyzed_functions
            ):
                lexical_name = " ".join(
                    analyzed_function.name_tokens
                )

                lexical_scope = " ".join(
                    analyzed_function.scope_tokens
                )

                lexical_docstring = " ".join(
                    analyzed_function.docstring_tokens
                )

                lexical_source = " ".join(
                    analyzed_function.identifier_tokens
                    + analyzed_function.comment_tokens
                    + analyzed_function.string_tokens
                )

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
                        scope_text,
                        docstring,
                        source_code,
                        lexical_name,
                        lexical_scope,
                        lexical_docstring,
                        lexical_source,
                        embedding
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        repository_path,
                        function.name,
                        function.filepath,
                        function.start_line,
                        function.end_line,
                        function.scope_path,
                        " ".join(function.scope_path or []),
                        function.docstring,
                        function.source_code,
                        lexical_name,
                        lexical_scope,
                        lexical_docstring,
                        lexical_source,
                        embedding
                    )
                )

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    def semantic_search(self, query_embedding, repository_path, limit=5):
        """Finds the most semantically similar code units using vector similarity."""
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

    def lexical_search(self, query_tokens, repository_path, limit=10):
        """Finds code units that match lexical query tokens using PostgreSQL full-text search."""
        cursor = self.connection.cursor()

        if len(query_tokens) == 0:
            cursor.close()
            return []

        ts_query = " | ".join(query_tokens)

        cursor.execute(
            """
            SELECT
                name,
                filepath,
                scope_path,
                start_line,
                ts_rank(
                    search_vector,
                    to_tsquery('simple', %s)
                ) AS score
            FROM code_units
            WHERE repository_path = %s
              AND search_vector @@ to_tsquery('simple', %s)
            ORDER BY score DESC
            LIMIT %s
            """,
            (
                ts_query,
                repository_path,
                ts_query,
                limit
            )
        )

        results = cursor.fetchall()
        cursor.close()

        return results

    def close(self):
        self.connection.close()