import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, LiteralString, Optional

from dotenv import load_dotenv
from neo4j import Query, Result
from pandas import DataFrame

from utils import logger, some

if TYPE_CHECKING:
    from driver.neo4j import Neo4jSession

_CONFIG_QUERY = (
    "CALL dbms.listConfig() "
    "YIELD name, value, description "
    "WHERE name = 'server.directories.neo4j_home' "
    "RETURN name, value, description; "
)


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


def _get_db_home(session: Neo4jSession) -> Optional[Path]:
    """
    Retrieve the _import_ and _home_ folders of the Neo4j database.

    :param session: Neo4j session to query the database.
    :type session: Neo4jSession
    :return: The value of `$NEO4J_HOME` (it's the main directory of the Neo4j instance used by the session in input).
    :rtype: Tuple[Path, Path] | None
    """
    try:
        result: Result = session.run_query(_CONFIG_QUERY)
        df: DataFrame = result.to_df()

        path: Any = df.loc[
            df["name"].str.endswith(".neo4j_home", na=False), "value"
        ].iloc[0]

        return Path(path)
    except Exception as error:
        logger.error(error)
        return None


if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")
    db_name: Optional[str] = os.environ.get("DB_NAME")

    if some(uri) and some(db_user) and some(db_password) and some(db_name):
        with Neo4jSession(uri, db_user, db_password, db_name) as session:
            result: Result = session.run_query(
                "CREATE (p:Person { born: $born, name: $name }) RETURN p",
                {"name": "Julius Trevam", "born": 1990},
            )

            df: DataFrame = result.to_df(expand=True)

        print(df)
