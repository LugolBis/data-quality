import os
from typing import Any, LiteralString, Optional

from dotenv import load_dotenv
from neo4j import Driver, EagerResult, GraphDatabase, Query, RoutingControl

from utils import some

load_dotenv()

uri: Optional[str] = os.environ.get("URI")
db_user: Optional[str] = os.environ.get("DB_USER")
db_password: Optional[str] = os.environ.get("DB_PW")


def run_query(
    driver: Driver,
    db_name: str,
    query: LiteralString,
    write_op: bool,
    parameters: Optional[dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> Optional[EagerResult]:
    query_prepared: Query = Query(text=query, metadata=parameters, timeout=timeout)

    if write_op:
        driver.execute_query(
            database_=db_name,
            query_=query_prepared,
            parameters_=parameters,
            routing_=RoutingControl.WRITE,
        )
        return None
    else:
        return driver.execute_query(
            database_=db_name,
            query_=query_prepared,
            parameters_=parameters,
            routing_=RoutingControl.READ,
        )


if __name__ == "__main__":
    if some(uri) and some(db_user) and some(db_password):
        with GraphDatabase.driver(uri, auth=(db_user, db_password)) as driver:
            run_query(
                driver,
                "movies",
                "CREATE (p:Person {name: 'Louis Dupont', born: 2020})",
                True,
            )
