import os
import time
from enum import Enum
from pathlib import Path
from typing import Optional

from neo4j_driver import Neo4jSession
from utils import logger, safe_exec, some


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


def load_from_script(
    session: Neo4jSession,
    script_path: Path,
    new_db_name: Optional[str] = None,
    overwrite_destination: bool = True,
) -> LoadResult:
    """
    Load a database from a **Cypher script** using `cypher-shell`.\n

    :param session: An active Neo4j session with sufficient privileges to create a new database
                    and execute the `dbms.listConfig()` procedure.
    :type session: Neo4jSession
    :param script_path: The absolute path of a cypher script.
    :type script_path: Path
    :param new_db_name: The optional name of the database if it's different from the `session` database.
    :type new_db_name: Optional[str]
    :param overwrite_destination: Remove all the **nodes** and **relationships**, but don't remove APOC procedures/functions/constraints.
    :type overwrite_destination: bool
    :return: The result of the load operation.
    :rtype: LoadResult
    """

    DELETE_QUERY = "MATCH (n) DETACH DELETE n;"
    command: list[str]

    if some(new_db_name):
        _create_database(session, new_db_name)

        with Neo4jSession.clone(session, new_db_name) as session_t:
            if overwrite_destination:
                session_t.run_query(DELETE_QUERY)
            command = session_t.get_cypher_shell_command(script_path)
    else:
        if overwrite_destination:
            session.run_query(DELETE_QUERY)
        command = session.get_cypher_shell_command(script_path)

    db_folder: Optional[Path] = session.get_home_folder()

    if some(db_folder):
        os.chdir(db_folder)

        if safe_exec(command):
            return LoadResult.LOAD_SUCCESS
        else:
            logger.error(f"Failed to execute the command : {' '.join(command)}")
            return LoadResult.LOAD_FAILED
    else:
        return LoadResult.NO_DB_HOME


def load_from_dump(
    session: Neo4jSession,
    dump_file_path: Path,
    rename: Optional[str] = None,
    overwrite_destination: bool = True,
    verbose: bool = True,
) -> LoadResult:
    """
    Load a **.dump** file into a Neo4j database.

    :param session: An active Neo4j session with sufficient privileges to create a new database
                    and execute the `dbms.listConfig()` procedure.
    :type session: Neo4jSession
    :param dump_file_path: Absolute file path to the the **.dump** file.
    :type dump_file_path: Path
    :param rename: To choose a database name different from that of the **.dump** file.
    :type rename: Optional[str]
    :param overwrite_destination: If `True` (default), overwrite the target database if it already exists.
    :type overwrite_destination: bool
    :param verbose: If `True` (default), enable detailed output when running the `neo4j-admin` command.
    :type verbose: bool
    :return: The result of the load operation.
    :rtype: LoadResult
    """
    dump_folder = dump_file_path.parent
    new_db_name: str

    if some(rename):
        os.rename(dump_file_path, os.path.join(dump_folder, f"{rename}.dump"))
        new_db_name = rename
    else:
        new_db_name = dump_file_path.name.removesuffix(".dump")

    _create_database(session, new_db_name)

    db_folder: Optional[Path] = session.get_home_folder()

    if some(db_folder):
        command: list[str] = [
            "./bin/neo4j-admin",
            "database",
            "load",
            f"--from-path={dump_folder}",
            new_db_name,
        ]

        if overwrite_destination:
            command.append("--overwrite-destination")

        if verbose:
            command.append("--verbose")

        session.close()

        return _load_with_admin(command, db_folder, new_db_name, recovery=False)
    else:
        return LoadResult.NO_DB_HOME


def load_from_csv(
    session: Neo4jSession,
    nodes: list[str],
    relationships: list[str],
    new_db_name: str,
    delimiter: str = ",",
    array_delimiter: str = ";",
    overwrite_destination: bool = True,
    verbose: bool = True,
) -> LoadResult:
    """
    Load **CSV** files into a Neo4j database.

    !!! CAUTION: The Neo4j instance is stopped and restarted during the process.
    The provided `session` will therefore no longer be valid after this function completes.

    :param session: An active Neo4j session with sufficient privileges to create a new database
                    and execute the `dbms.listConfig()` procedure.
    :type session: Neo4jSession
    :param nodes: A list of absolute paths to CSV files containing node data.
    :type nodes: list[str]
    :param relationships: A list of absolute paths to CSV files containing relationship data.
    :type relationships: list[str]
    :param new_db_name: The target database used to perform the import.
                        It may or may not already exist.
    :type new_db_name: str
    :param delimiter: The delimiter used to separate header fields and values in the CSV files.
    :type delimiter: str
    :param array_delimiter: The delimiter used for array values within CSV fields.
    :type array_delimiter: str
    :param overwrite_destination: If `True` (default), overwrite the target database if it already exists.
    :type overwrite_destination: bool
    :param verbose: If `True` (default), enable detailed output when running the `neo4j-admin` command.
    :type verbose: bool
    :return: The result of the load operation.
    :rtype: LoadResult
    """

    _create_database(session, new_db_name)

    db_folder: Optional[Path] = session.get_home_folder()

    if some(db_folder):
        command: list[str] = [
            "./bin/neo4j-admin",
            "database",
            "import",
            "full",
            new_db_name,
            f"--delimiter={delimiter}",
            f"--array-delimiter={array_delimiter}",
        ]

        if len(nodes) > 0:
            command.append(f"--nodes={','.join(nodes)}")

        if len(relationships) > 0:
            command.append(f"--relationships={','.join(relationships)}")

        if overwrite_destination:
            command.append("--overwrite-destination")

        if verbose:
            command.append("--verbose")

        session.close()

        return _load_with_admin(command, db_folder, new_db_name, recovery=True)
    else:
        return LoadResult.NO_DB_HOME


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
