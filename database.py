import psycopg
from pgvector.psycopg import register_vector


class Database:
    def __init__(self):
        self.connection = psycopg.connect("dbname=pyseek")
        register_vector(self.connection)

    def replace_file_functions(
            self,
            cursor,
            indexed_file_id,
            functions,
            embeddings,
            analyzed_functions
    ):
        """
        Replaces all code units belonging to one indexed file.
        """

        cursor.execute(
            """
            DELETE FROM code_units
            WHERE indexed_file_id = %s
            """,
            (indexed_file_id,)
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
                    indexed_file_id,
                    name,
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
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    indexed_file_id,
                    function.name,
                    function.start_line,
                    function.end_line,
                    function.scope_path,
                    " ".join(
                        function.scope_path or []
                    ),
                    function.docstring,
                    function.source_code,
                    lexical_name,
                    lexical_scope,
                    lexical_docstring,
                    lexical_source,
                    embedding
                )
            )

    def replace_indexed_file(
            self,
            repository_path,
            filepath,
            content_hash,
            index_version,
            functions,
            embeddings,
            analyzed_functions
    ):
        """
        Atomically updates an indexed file and all
        code units extracted from it.
        """

        cursor = self.connection.cursor()

        try:
            indexed_file_id = self.upsert_indexed_file(
                cursor,
                repository_path,
                filepath,
                content_hash,
                index_version
            )

            self.replace_file_functions(
                cursor,
                indexed_file_id,
                functions,
                embeddings,
                analyzed_functions
            )

            self.connection.commit()

            return indexed_file_id

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
            SELECT
                cu.name,
                f.filepath,
                cu.scope_path,
                cu.start_line,
                1 - (cu.embedding <=> %s) AS score
            FROM code_units cu
            JOIN indexed_files f
                ON cu.indexed_file_id = f.id
            WHERE f.repository_path = %s
            ORDER BY cu.embedding <=> %s
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
                cu.name,
                f.filepath,
                cu.scope_path,
                cu.start_line,
                ts_rank(
                    cu.search_vector,
                    to_tsquery('simple', %s)
                ) AS score
            FROM code_units cu
            JOIN indexed_files f
                ON cu.indexed_file_id = f.id
            WHERE f.repository_path = %s
              AND cu.search_vector @@ to_tsquery('simple', %s)
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

    def get_indexed_files(self, repository_path):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                filepath,
                content_hash,
                index_version
            FROM indexed_files
            WHERE repository_path = %s
            """,
            (repository_path,)
        )

        rows = cursor.fetchall()
        cursor.close()

        return rows

    def delete_indexed_file(self, indexed_file_id):
        """Deletes an indexed file that no longer exists in the repository."""
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM indexed_files
                WHERE id = %s
                """,
                (indexed_file_id,)
            )

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    #insert the file in the db if it's new in the repo, or updates it if it
    def upsert_indexed_file(
            self,
            cursor,
            repository_path,
            filepath,
            content_hash,
            index_version
    ):
        """
        Creates a new indexed_files row or updates
        the existing one.

        Returns the indexed_file id.
        """

        cursor.execute(
            """
            INSERT INTO indexed_files
            (
                repository_path,
                filepath,
                content_hash,
                index_version
            )
            VALUES (%s, %s, %s, %s)
    
            ON CONFLICT (repository_path, filepath)
            DO UPDATE SET
                content_hash = EXCLUDED.content_hash,
                index_version = EXCLUDED.index_version,
                indexed_at = CURRENT_TIMESTAMP
    
            RETURNING id
            """,
            (
                repository_path,
                filepath,
                content_hash,
                index_version
            )
        )

        indexed_file_id = cursor.fetchone()[0]

        return indexed_file_id

    def close(self):
        self.connection.close()