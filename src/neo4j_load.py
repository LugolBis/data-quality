import os
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from neo4j import Result
from pandas import DataFrame

from neo4j_driver import Neo4jSession
from utils import logger, safe_exec, some

_CONFIG_QUERY = (
    "CALL dbms.listConfig()"
    "YIELD name, value, description"
    "WHERE name = 'server.directories.neo4j_home'"
    "RETURN name, value, description;"
)


class _InstanceAction(Enum):
    """
    Enumeration to choose which action to apply to the Neo4j instance.
    """

    START = "start"
    STOP = "stop"


class LoadResult(Enum):
    """
    Enumeration to describe the Load Result.
    """

    NO_DB_HOME = "failed to get the Neo4j instance home folder"
    LOAD_SUCCESS = "successfully loaded the data"
    STOP_FAILED = "failed to stop the instance to import the data"
    START_FAILED = "failed to restart the database after the import"
    RECOVERY_SUCCESS = "successfully recovery the database after the failed import"
    RECOVERY_FAILED = "failed to recovery the database"


def load_from_dump():
    # TODO ! Implement a function to load `.dumps` files format
    pass


def load_from_csv(
    session: Neo4jSession,
    nodes: list[str],
    relationships: list[str],
    new_db_name: str,
    delimiter: str = ";",
    array_delimiter: str = ",",
    overwrite_destination: bool = False,
    verbose: bool = True,
) -> LoadResult:
    try:
        session.run_query("CREATE DATABASE $name", {"name": new_db_name})
    except Exception as error:
        logger.error(error)

    db_folder = _get_db_home(session)

    if some(db_folder):
        os.chdir(db_folder)

        command = [
            "../bin/neo4j-admin",
            "database",
            "import",
            "full",
            new_db_name,
            f"--delimiter={delimiter}",
            f"--array-delimiter={array_delimiter}",
            "--nodes",
            ",".join(nodes),
            "--relationships",
            ",".join(relationships),
        ]

        if overwrite_destination:
            command.append("--overwrite-destination")

        if verbose:
            command.append("--verbose")

        session.close()
        del session

        if _alter_instance(db_folder, _InstanceAction.STOP):
            if safe_exec(command):
                return (
                    LoadResult.LOAD_SUCCESS
                    if _alter_instance(db_folder, _InstanceAction.START)
                    else LoadResult.START_FAILED
                )
            else:
                logger.error(f"Failed to execute the command : {' '.join(command)}")
                return (
                    LoadResult.RECOVERY_SUCCESS
                    if _recovery_database(db_folder, new_db_name)
                    else LoadResult.RECOVERY_FAILED
                )
        else:
            logger.error("Failed to stop the Neo4j instance.")
            return LoadResult.STOP_FAILED
    else:
        return LoadResult.NO_DB_HOME


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

        path = df.loc[df["name"].str.endswith(".neo4j_home", na=False), "value"].iloc[0]

        return Path(path)
    except Exception as error:
        logger.error(error)
        return None


def _alter_instance(db_home_folder: Path, action: _InstanceAction) -> bool:
    """
    Execute one of the `_InstanceAction` to alter the `Neo4j` instance status.

    :param db_home_folder: Home folder of the Neo4j instance.
    :type db_home_folder: Path
    :param action: Action to be executed on the instance.
    :type action: _InstanceAction
    :return: If the bash command success.
    :rtype: bool
    """
    neo4j_exec = os.path.join(db_home_folder, "bin", "neo4j")
    command: list[str] = [neo4j_exec]

    match action:
        case _InstanceAction.START:
            command.append("start")
        case _InstanceAction.STOP:
            command.append("stop")
        case _:
            logger.error(f"Incosistant _InstanceAction : {action}")
            return False

    return safe_exec(command)


def _recovery_database(db_home_folder: Path, db_name: str) -> bool:
    # TODO! Implement a way to use `neo4j-admin to import empty nodes to recovery the database.`
    return False


if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")

    if some(uri) and some(db_user) and some(db_password):
        with Neo4jSession(uri, db_user, db_password, "neo4j") as session:
            print(_get_db_home(session))
