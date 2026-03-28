import os

from dotenv import load_dotenv

from driver.neo4j_driver import Neo4jSession
from tests import (
    completeness,
    consistency,
    integrity,
    labeling,
    lisibility,
    outliers,
    uniqueness,
    validity,
)
from utils.utils import some

if __name__ == "__main__":
    load_dotenv()

    uri: str | None = os.environ.get("URI")
    db_user: str | None = os.environ.get("DB_USER")
    db_password: str | None = os.environ.get("DB_PW")
    db_name: str | None = os.environ.get("DB_NAME")

    if some(uri) and some(db_user) and some(db_password) and some(db_name):
        with Neo4jSession(uri, db_user, db_password, db_name) as session:
            completeness.main(session)
            consistency.main(session)
            integrity.main(session)
            labeling.main(session)
            lisibility.main(session)
            outliers.main(session)
            uniqueness.main(session)
            validity.main(session)
