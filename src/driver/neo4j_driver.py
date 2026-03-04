from pathlib import Path
from typing import TYPE_CHECKING, Any, LiteralString, Self

from neo4j import Driver, GraphDatabase, Query, Result, Session

from utils.utils import logger, some

if TYPE_CHECKING:
    from pandas import DataFrame

_CONFIG_QUERY = (
    "CALL dbms.listConfig() "
    "YIELD name, value, description "
    "WHERE name = 'server.directories.neo4j_home' "
    "RETURN name, value, description; "
)


class Neo4jSession:
    """
    Neo4jSession is a class to wrap the logic of the Neo4j API to produce more concise
    code.\n
    Note : It is hardly recommanded to use this class in a ***with*** clause.
    """

    def __init__(self, uri: str, user: str, password: str, database: str) -> None:
        """
        Init the object with the arguments took in input, who are used to open a
        `neo4j.Driver` and `neo4j.Session` connection.

        :param self: The object itself.
        :param uri: URI of the Neo4j instance.
        :type uri: str
        :param user: User used to query the database.
        :type user: str
        :param password: Password of the `user`.
        :type password: str
        :param database: Database name.
        :type database: str
        """

        self._uri: str = uri
        self._user: str = user
        self._password: str = password
        self._database: str = database
        self._driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session: Session = self._driver.session(database=database)
        self._closed: bool = False
        self._home_folder: Path | None = None

    @classmethod
    def clone(
        cls,
        session: Neo4jSession,
        database: str | None = None,
    ) -> Neo4jSession:
        """
        Clone the `Neo4jSession` took in argument and change the database if `database`
        is not 'None'.

        :param cls: The class name.
        :param session: The session who's need to be clone.
        :type session: Neo4jSession
        :param database: If you want to change the database of the `session`.
        :type database: Optional[str]
        :return: The exact same `Neo4jSession` as `session` or a session connected to
        the `database` took in argument.
        :rtype: Neo4jSession
        """
        cloned_database: str

        cloned_database = database if some(database) else session._database

        return Neo4jSession(
            session._uri,
            session._user,
            session._password,
            cloned_database,
        )

    def get_home_folder(self) -> Path | None:
        """
        Use it to retrieve the absolute file path of the home database folder of
        the current session.

        :param self: A `Neo4jSession` object.
        :return: Description
        :rtype: Path | None
        """
        if not some(self._home_folder):
            self._home_folder = _get_db_home(self)
        return self._home_folder

    def __enter__(self) -> Self:
        """
        Overload the `__enter__` who's provide to use the `Neo4jSession` in
        ***with*** clause.

        :param self: A `Neo4jSession` object.
        """
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        """
        Overload the `__enter__` who's provide to use the `Neo4jSession` in
        ***with*** clause.

        :param self: A `Neo4jSession` object.
        """
        self.close()

    def __del__(self) -> None:
        """
        Automatically close the connection when the object is deleted.\n
        !! CAUTION : Sometimes it isn't called by python, so i hardly recommand to use
        the ***with*** clause.

        :param self: A `Neo4jSession` object.
        """
        self.close()

    def close(self) -> None:
        """
        Call the method `.close()` on both object `neo4j.Driver` and `neo4j.Session`.

        :param self: A `Neo4jSession` object.
        """
        if not self._closed:
            if not self._session.closed():
                self._session.close()
            self._driver.close()

        self._closed = True

    def _reopen(self) -> None:
        """
        Try to reopen the session (it's called by `.runquery()` after a massive loading
        who stop/restart the Neo4j insatnce and automatically close all the sessions).

        :param self: A `Neo4jSession` object.
        """
        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
            )
            self._session = self._driver.session(database=self._database)
            self._closed = False
        except Exception as error:
            logger.error(error)

    def run_query(
        self,
        query: LiteralString,
        parameters: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Result:
        """
        Get a **Lazy result** of a **Cypher** query with both READ/WRITE rights.\n
        Note : it automatically try to use `.reopen()` method when the session is closed

        :param self: A `Neo4jSession` object.
        :param query: Cypher query.
        :type query: LiteralString
        :param parameters: Parameters passed to `neo4j.Session.run(parameters=)`
        :type parameters: Optional[dict[str, Any]]
        :param timeout: Timeouit before cancel a query.
        :type timeout: Optional[float]
        :return: **Lazy result** which could be easily transformed as a **Graph** or a
        **pandas.DataFrame**.
        :rtype: Result
        """
        kwargs: dict[str, Any] = _prepare_query(query, parameters, timeout)

        if self._closed:
            self._reopen()

        return self._session.run(**kwargs)

    def get_cypher_shell_command(self, script_path: Path | None) -> list[str]:
        """
        Generate the `cypher-shell` command to query the database of the session.\n
        Note : you can use it to execute Cypher scripts.

        :param self: A `Neo4jSession` object.
        :param script_path: Path of a Cypher script
        :type script_path: Optional[Path]
        :return: The `cypher-shell` command.
        :rtype: list[str]
        """

        command: list[str] = [
            "./bin/cypher-shell",
            "--address",
            self._uri,
            "--username",
            self._user,
            "--password",
            self._password,
            "--database",
            self._database,
        ]

        if some(script_path):
            command.extend(["--file", str(script_path)])

        return command


def _prepare_query(
    query: LiteralString,
    parameters: dict[str, Any] | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    """
    Format the arguments took in input as the `neo4j.Session.run()` arguments format.

    :param query: Cypher query.
    :type query: LiteralString
    :param parameters: Parameters passed to `neo4j.Session.run(parameters=)`
    :type parameters: Optional[dict[str, Any]]
    :param timeout:Timeouit before cancel a query.
    :type timeout: Optional[float]
    :return: Parameters formated.
    :rtype: dict[str, Any]
    """
    query_prepared = Query(text=query, timeout=timeout)

    return {
        "query": query_prepared,
        "parameters": parameters,
    }


def _get_db_home(session: Neo4jSession) -> Path | None:
    """
    Retrieve the _import_ and _home_ folders of the Neo4j database.

    :param session: Neo4j session to query the database.
    :type session: Neo4jSession
    :return: The value of `$NEO4J_HOME` (it's the main directory of the Neo4j instance
    used by the session in input).
    :rtype: Tuple[Path, Path] | None
    """
    try:
        result: Result = session.run_query(_CONFIG_QUERY)
        df: DataFrame = result.to_df()

        path: Any = df.loc[
            df["name"].str.endswith(".neo4j_home", na=False),
            "value",
        ].iloc[0]

        return Path(path)
    except Exception as error:
        logger.error(error)
        return None
