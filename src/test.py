import os
from typing import Optional

from dotenv import load_dotenv

import tests.consistency as consistency
import tests.integrity as integrity
import tests.lisibility as lisibility
import tests.schema as schema
from driver.neo4j_driver import Neo4jSession
from utils.utils import some

if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")
    db_name: Optional[str] = os.environ.get("DB_NAME")

    if some(uri) and some(db_user) and some(db_password) and some(db_name):
        with Neo4jSession(uri, db_user, db_password, db_name) as session:
            integrity.main(session)
            schema.main(session)
            consistency.main(session)
            lisibility.main(session)
