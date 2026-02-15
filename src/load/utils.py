import os
import time
from enum import Enum
from pathlib import Path

from driver.neo4j import Neo4jSession
from utils import logger, safe_exec


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
    LOAD_SUCCESS = "successfully to load the data"
    LOAD_FAILED = "failed to load the data"
    STOP_FAILED = "failed to stop the instance to import the data"
    START_FAILED = "failed to restart the database after the import"
    RECOVERY_SUCCESS = "successfully recovery the database after the failed import"
    RECOVERY_FAILED = "failed to recovery the database"


def _load_with_admin(
    command: list[str], db_folder: Path, new_db_name: str, recovery: bool = True
) -> LoadResult:
    """
    Execute the `neo4j-admin` command took in input with `command` to be executed from the home folder of the database (`db_folder`).

    Note : `recovery` parameter permite you to choose if the failure of your command need to recovery the database.

    :param command: The `neo4j-admin` shell command.
    :type command: list[str]
    :param db_folder: Home folder of the Neo4j instance.
    :type db_folder: Path
    :param new_db_name: Name of the database to create.
    :type new_db_name: str
    :param recovery: If the failure of the command need to recovery the database.
    :type recovery: bool
    :return: The result of the load operation.
    :rtype: LoadResult
    """
    os.chdir(db_folder)

    if _alter_instance(db_folder, _InstanceAction.STOP):
        if safe_exec(command):
            return (
                LoadResult.LOAD_SUCCESS
                if _alter_instance(db_folder, _InstanceAction.START)
                else LoadResult.START_FAILED
            )
        else:
            logger.error(f"Failed to execute the command : {' '.join(command)}")
            if recovery:
                return (
                    LoadResult.RECOVERY_SUCCESS
                    if _recovery_database(db_folder, new_db_name)
                    else LoadResult.RECOVERY_FAILED
                )
            else:
                return LoadResult.RECOVERY_SUCCESS
    else:
        logger.error("Failed to stop the Neo4j instance.")
        return LoadResult.STOP_FAILED


def _create_database(
    session: Neo4jSession, new_db_name: str, timeout: int = 60
) -> None:
    """
    Create a new database called `new_db_name`.\n
    Note : Your user's session needs to have the rights to create a new database.

    :param session: Neo4j session to query the database.
    :type session: Neo4jSession
    :param new_db_name: Name of the database to create.
    :type new_db_name: str
    :param timeout: Timeout before end to try to check if the database is online.
    :type timeout: int
    """
    try:
        session.run_query("CREATE DATABASE $name", {"name": new_db_name})

        while timeout > 0:
            result = session.run_query(
                "SHOW DATABASE $db_name", {"db_name": new_db_name}
            )
            record = result.single()

            if record and record["currentStatus"] == "online":
                break

            time.sleep(1)
            timeout -= 1
    except Exception as _:
        pass


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
    neo4j_exec: str = os.path.join(db_home_folder, "bin", "neo4j")
    command: list[str] = [neo4j_exec]

    match action:
        case _InstanceAction.START:
            command.append("start")
        case _InstanceAction.STOP:
            command.append("stop")
        case _:
            logger.error(f"Incosistant _InstanceAction : {action}")
            return False

    result: bool = safe_exec(command)
    if not result:
        logger.error(f"Failed to execute the command : {' '.join(command)}")

    return result


def _recovery_database(db_home_folder: Path, db_name: str) -> bool:
    """
    Process an empty import to the database to recovery it.\n
    Note : Use it to recovery your database after a failed import and assert the *Neo4j* instance is stopped before call this function.

    :param db_home_folder: Absolute path of the Neo4j instance's home folder.
    :type db_home_folder: Path
    :param db_name: The name of the database who need to be recoveried.
    :type db_name: str
    :return: If the database was successfully recovery.
    :rtype: bool
    """
    os.chdir(db_home_folder)
    path: str = os.path.join(db_home_folder, "import", "RECOVERY.csv")

    command: list[str] = [
        "./bin/neo4j-admin",
        "database",
        "import",
        "full",
        db_name,
        "--delimiter=;",
        "--array-delimiter=,",
        f"--nodes={path}",
        "--overwrite-destination",
    ]

    with open(path, "w") as fd:
        fd.write(":ID;:LABEL")

    result: bool = safe_exec(command)
    if not result:
        logger.error(f"Failed to execute the command : {' '.join(command)}")

    os.remove(path)

    return result
