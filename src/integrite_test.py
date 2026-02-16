import os
from typing import Optional

from dotenv import load_dotenv

from driver.neo4j_driver import Neo4jSession
from quality.integrity import check_properties_consistency, detecter_doublons
from utils.utils import some

if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")
    db_name: Optional[str] = os.environ.get("DB_NAME")

    if some(uri) and some(db_user) and some(db_password) and some(db_name):
        with Neo4jSession(uri, db_user, db_password, db_name) as session:
            properties = check_properties_consistency(session)
            similarities = detecter_doublons(session, seuil_similarite=0.6)

            if some(properties):
                print(properties)

            if some(similarities):
                print("\n")
                print("\n".join([sim.__repr__() for sim in similarities]))
