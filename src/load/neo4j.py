import os
from pathlib import Path
from typing import Optional

from driver.neo4j_driver import Neo4jSession
from load.enums import LoadResult
from load.utils import _create_database, _load_with_admin
from utils.utils import logger, safe_exec, some


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
