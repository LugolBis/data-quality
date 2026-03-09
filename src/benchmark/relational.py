from pathlib import Path
from typing import TYPE_CHECKING

from load.enums import _InstanceAction
from load.utils import _alter_instance, _create_database
from utils.utils import logger, safe_exec

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from driver.postgres import PostgresSession


def neo4j_migrator_cmd(
    postgre_config: dict[str, str],
    neo4j_dbname: str,
    neo4j_import_folder: str,
    output_dir: str,
) -> list[str]:
    return [
        "neo4j-migrator",
        f"-pg_host={postgre_config['host']}",
        f"-pg_port={postgre_config['port']}",
        f"-pg_user={postgre_config['user']}",
        f"-pg_password={postgre_config['password']}",
        f"-pg_database={postgre_config['dbname']}",
        f"-neo4j_database={neo4j_dbname}",
        f"-neo4j_import_folder={neo4j_import_folder}",
        f"-work_folder={output_dir}",
        "--ni",
    ]


def etl_graph(
    postgres_s: PostgresSession,
    neo4j_s: Neo4jSession,
    output_dir: str,
) -> bool:
    folder_path: Path = Path(output_dir)

    if not Path.exists(folder_path):
        try:
            Path.mkdir(folder_path, parents=True)
        except OSError as e:
            logger.error(e)

    postgre_config: dict[str, str] = postgres_s.get_config()
    neo4j_home_folder: Path | None = neo4j_s.get_home_folder()

    if neo4j_home_folder is not None:
        neo4j_import_folder = neo4j_home_folder.joinpath("import/")
    else:
        logger.error("Failed to retrieve Neo4j database import folder.")
        return False

    new_db_name = f"{postgre_config['dbname']}-relational"
    _create_database(neo4j_s, new_db_name)

    if _alter_instance(neo4j_home_folder, _InstanceAction.STOP):
        command = neo4j_migrator_cmd(
            postgre_config,
            new_db_name,
            str(neo4j_import_folder) + "/",
            output_dir,
        )

        if not safe_exec(command, output=True):
            logger.error("Failed to execute the neo4j-migrator command.")
            return False

        return _alter_instance(neo4j_home_folder, _InstanceAction.START)
    logger.error("Failed to stop the Neo4j instance.")
    return False
