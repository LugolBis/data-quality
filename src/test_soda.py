from benchmark.soda import main
from driver.postgres import PostgresSession
from utils.utils import some

if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    dbname: str | None = os.environ.get("PG_DBNAME")
    user: str | None = os.environ.get("PG_USER")
    password: str | None = os.environ.get("PG_PASSWORD")
    host: str | None = os.environ.get("PG_HOST")
    port: str | None = os.environ.get("PG_PORT")

    if some(dbname) and some(user) and some(host) and some(port):
        if password is None:
            password = ""

        with PostgresSession(dbname, user, password, host, port) as session:
            main(session, "Data/soda")
    else:
        print("Inconsistant PostgreSQL config.")
