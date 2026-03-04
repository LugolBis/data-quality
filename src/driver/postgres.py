from typing import Any, Self

import psycopg2 as pg


class PostgresSession:
    """
    This class is a wrapper around `psycopg2.Connection` and `psycopg2.Cursor`.
    """

    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: str = "5432",
    ) -> None:
        """
        Initialize a new PostgreSQL `Connection` and `Cursor`.

        :param self: The object itself.
        :param dbname: The target database.
        :type dbname: str
        :param user: The user used to connect to the database.
        :type user: str
        :param password: The password used.
        :type password: str
        :param host: The host of the database.
        :type host: str
        :param port: The database port. (default: 5432)
        :type port: int
        """

        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._closed = False

        self._conn = pg.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )

    def get_config(self) -> dict[str, str]:
        return {
            "dbname": self._dbname,
            "user": self._user,
            "password": self._password,
            "host": self._host,
            "port": self._port,
        }

    def __enter__(self) -> Self:
        """
        Overload the `__enter__` who's provide to use the `Neo4jSession` in
        ***with*** clause.

        :param self: A `Neo4jSession` object.
        """
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        """
        Overload the `__enter__` who's provide to use the `PostgresSession` in
        ***with*** clause.

        :param self: A `PostgresSession` object.
        """
        self.close()

    def __del__(self) -> None:
        """
        Automatically close the connection when the object is deleted.\n
        !! CAUTION : Sometimes it isn't called by python, so i hardly recommand to use
        the ***with*** clause.

        :param self: A `PostgresSession` object.
        """
        self.close()

    def close(self) -> None:
        """
        Call the method `.close()` on `psycopg2.Connection` object.

        :param self: A `PostgresSession` object.
        """
        if not self._closed:
            self._conn.close()

        self._closed = True

    def execute(self, statement: str) -> None:
        """
        Execute a SQL statement without returning any result.

        :param self: The `PostgresSession` object itself.
        :param statement: A PostgreSQL statement.
        :type statement: str
        """

        with self._conn.cursor() as cursor:
            cursor.execute(query=statement)

    def query(self, query: str) -> list[tuple[Any, ...]]:
        """
        Execute a SQL query an return all the values retrieved.

        :param self: The `PostgresSession` object itself.
        :param query: A PostgreSQL query.
        :type query: str
        :return: A list of tuples which ones are the rows.
        :rtype: list[tuple[Any]]
        """

        result: list[tuple[Any, ...]]
        with self._conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result
