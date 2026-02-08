import os
from typing import Any, LiteralString, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query, Result
from pandas import DataFrame

from utils import some


class Neo4jSession:
    """
    Neo4jSession is a class to wrap the logic of the Neo4j API to produce more concise code.\n
    Note : It is hardly recommanded to use this class in a ***with*** clause.
    """

    def __init__(self, uri: str, user: str, password: str, database: str) -> None:
        """
        Init the object with the arguments took in input, who are used to open a `neo4j.Driver` and `neo4j.Session` connection.

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
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session = self._driver.session(database=database)
        self._closed = False

    def __enter__(self):
        """
        Overload the `__enter__` who's provide to use the `Neo4jSession` in ***with*** clause.

        :param self: Description
        """
        return self

    def __exit__(self, exc_type, exc, tb):
        """
        Overload the `__enter__` who's provide to use the `Neo4jSession` in ***with*** clause.

        :param self: Description
        """
        self.close()

    def __del__(self):
        """
        Automatically close the connection when the object is deleted.\n
        /!\ Attention : Sometimes it isn't called by python, so i hardly recommand to use the ***with*** clause.

        :param self: Description
        """
        self.close()

    def close(self) -> None:
        """
        Call the method `.close()` on both object `neo4j.Driver` and `neo4j.Session`.

        :param self: Description
        """
        if not self._closed:
            if not self._session.closed():
                self._session.close()
            self._driver.close()

    def run_query(
        self,
        query: LiteralString,
        parameters: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Result:
        """
        Get a **Lazy result** of a **Cypher** query with both READ/WRITE rights.

        :param self: The object itself.
        :param query: Cypher query.
        :type query: LiteralString
        :param parameters: Parameters passed to `neo4j.Session.run(parameters=)`
        :type parameters: Optional[dict[str, Any]]
        :param timeout: Timeouit before cancel a query.
        :type timeout: Optional[float]
        :return: **Lazy result** which could be easily transformed as a **Graph** or a **pandas.DataFrame**.
        :rtype: Result
        """
        kwargs: dict[str, Any] = _prepare_query(query, parameters, timeout)
        return self._session.run(**kwargs)


def _prepare_query(
    query: LiteralString,
    parameters: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
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


if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")

    if some(uri) and some(db_user) and some(db_password):
        with Neo4jSession(uri, db_user, db_password, "movies") as session:
            result: Result = session.run_query(
                "CREATE (p:Person { born: $born, name: $name }) RETURN p",
                {"name": "Julius Trevam", "born": 1990},
            )

            df: DataFrame = result.to_df(expand=True)

        print(df)
