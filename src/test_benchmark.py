from benchmark.relational import etl_graph
from benchmark.soda import scoring
from driver.neo4j_driver import Neo4jSession
from driver.postgres import PostgresSession
from utils.utils import some

if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    # Load Neo4j variables :
    neo4j_uri: str | None = os.environ.get("URI")
    neo4j_user: str | None = os.environ.get("DB_USER")
    neo4j_password: str | None = os.environ.get("DB_PW")
    neo4j_name: str | None = os.environ.get("DB_NAME")

    # Load PostgreSQL variables :
    pg_dbname: str | None = os.environ.get("PG_DBNAME")
    pg_user: str | None = os.environ.get("PG_USER")
    pg_password: str | None = os.environ.get("PG_PASSWORD")
    pg_host: str | None = os.environ.get("PG_HOST")
    pg_port: str | None = os.environ.get("PG_PORT")

    if some(pg_dbname) and some(pg_user) and some(pg_host) and some(pg_port):
        if pg_password is None:
            pg_password = ""

        with PostgresSession(
            pg_dbname,
            pg_user,
            pg_password,
            pg_host,
            pg_port,
        ) as session_pg:
            # Test Soda module
            quality_score = scoring(session_pg, "Data/soda")
            print(f"Data Quality Score : {quality_score * 100}%")  # noqa: T201

            # Test Relational module
            if (
                some(neo4j_uri)
                and some(neo4j_user)
                and some(neo4j_password)
                and some(neo4j_name)
            ):
                with Neo4jSession(
                    neo4j_uri,
                    neo4j_user,
                    neo4j_password,
                    neo4j_name,
                ) as session_neo4j:
                    if etl_graph(session_pg, session_neo4j, "Data/relational"):
                        print(
                            "Successfully transform a Relational database into a Graph "
                            "database using neo4j-migrator",
                        )
                    else:
                        print(
                            "Failed to transform a Relational database into a Graph "
                            "database using neo4j-migrator",
                        )
    else:
        print("Inconsistant PostgreSQL config.")  # noqa: T201
