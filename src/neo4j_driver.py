import os
from typing import Any, LiteralString, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query, RoutingControl

from utils import some


def prepare_query(
    db_name: str,
    query: LiteralString,
    write_op: bool,
    parameters: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> dict[str, Any]:
    query_prepared = Query(text=query, timeout=timeout)
    routing: RoutingControl

    if write_op:
        routing = RoutingControl.WRITE
    else:
        routing = RoutingControl.READ

    return {
        "database_": db_name,
        "query_": query_prepared,
        "parameters_": parameters,
        "routing_": routing,
    }


if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")

    if some(uri) and some(db_user) and some(db_password):
        with GraphDatabase.driver(uri, auth=(db_user, db_password)) as driver:
            parameters = prepare_query(
                "movies",
                "MATCH (p: Person)-[r]-(e2) RETURN p, r, e2 LIMIT $lim",
                False,
                {"label": "Person", "lim": 25},
            )

            driver.execute_query(**parameters)
