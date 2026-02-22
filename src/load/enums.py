from enum import Enum


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

    NO_DB_HOME = "Failed to get the Neo4j instance home folder."
    LOAD_SUCCESS = "Successfully to load the data."
    LOAD_FAILED = "Failed to load the data."
    STOP_FAILED = "Failed to stop the instance to import the data."
    START_FAILED = "Failed to restart the database after the import."
    RECOVERY_SUCCESS = "Successfully recovery the database after the failed import."
    RECOVERY_FAILED = "Failed to recovery the database."
