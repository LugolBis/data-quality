import os
from typing import Any, LiteralString, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query, Result
from pandas import DataFrame

from utils import some


class Neo4jSession:
    def __init__(self, uri: str, username: str, password: str, database: str) -> None:
        self._driver = GraphDatabase.driver(uri, auth=(username, password))
        self._session = self._driver.session(database=database)
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self) -> None:
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
        kwargs: dict[str, Any] = _prepare_query(query, parameters, timeout)
        return self._session.run(**kwargs)


def _prepare_query(
    query: LiteralString,
    parameters: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> dict[str, Any]:
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
