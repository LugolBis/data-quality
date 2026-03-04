import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from utils.utils import logger

if TYPE_CHECKING:
    from driver.postgres import PostgresSession

TYPE_MAPPING: dict[str, str] = {
    "smallint": "smallint",
    "integer": "integer",
    "real": "real",
    "character varying": "varchar",
    "text": "text",
    "date": "date",
    "bytea": "binary",
}

BASE_DIR: Path = Path(__file__).resolve().parent
PG_META_SCRIPT: Path = BASE_DIR.joinpath(
    "postgresql/meta_data.sql",
)


def _map_postgres_type(pg_type: str) -> str:
    """
    Map PostgreSQL types to Soda contract types.

    :param pg_type: PostgreSQL type extracted from meta data.
    :type pg_type: str
    :return: The equivalent **Soda** type.
    :rtype: str

    """

    return TYPE_MAPPING.get(pg_type, pg_type)


def _generate_config(
    host: str,
    user: str,
    password: str,
    database: str,
) -> dict[str, Any]:
    return {
        "type": "postgres",
        "name": f"pg_{database}",
        "connection": {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        },
    }


def _generate_contract(ds_name: str, table_metadata: dict) -> dict:
    table_name = table_metadata["table_name"]

    contract = {
        "dataset": f"{ds_name}/{table_name}",
        "columns": [],
    }

    for column in table_metadata["columns"]:
        column_def = {
            "name": column["column_name"],
            "data_type": _map_postgres_type(column["data_type"]),
            "checks": [],
        }

        missing = False

        # NOT NULL constraint
        if column["is_nullable"] == "NO":
            column_def["checks"].append({"missing": {}})
            missing = True

        # PRIMARY KEY (Uniqueness + NOT NULL) constraint
        if column.get("primary_key"):
            if not missing:
                column_def["checks"].append({"missing": {}})
            column_def["checks"].append({"duplicate": {}})

        # FOREIGN KEY constraint
        if column.get("foreign_key"):
            for fk in column["foreign_key"]:
                fk_check = {
                    "invalid": {
                        "valid_reference_data": {
                            "dataset": f"{ds_name}/{fk['referenced_table']}",
                            "column": fk["referenced_column"],
                        },
                    },
                }
                column_def["checks"].append(fk_check)

        # Remove empty checks keys
        if not column_def["checks"]:
            del column_def["checks"]

        contract["columns"].append(column_def)

    return contract


def main(
    session: PostgresSession,
    output_dir: str,
) -> None:
    conf = session.get_config()
    dbname = conf["dbname"]

    with PG_META_SCRIPT.open("r") as fs:
        meta_query: str = fs.read()
        row: tuple[Any, ...] = session.query(meta_query)[0]

        if isinstance(row[0], str):
            metadata = json.loads(row[0])
        elif isinstance(row[0], list):
            metadata = row[0]
        else:
            logger.error(f"Invalid row : {row}")
            return

    output_path = Path(output_dir).joinpath(dbname)
    output_path.mkdir(parents=True, exist_ok=True)

    with Path(output_path.joinpath(f"{dbname}_config.yml")).open("w") as fd:
        yaml.dump(
            _generate_config(
                host=conf["host"],
                user=conf["user"],
                password=conf["password"],
                database=dbname,
            ),
            fd,
            sort_keys=False,
        )

    for table in metadata:
        contract = _generate_contract(f"pg_{conf['dbname']}", table)

        file_path = output_path.joinpath(f"{table['table_name']}_contract.yml")

        with Path(file_path).open("w") as fd:
            yaml.dump(contract, fd, sort_keys=False)

        logger.info(f"Generated: {file_path}")
