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

    NO_DB_HOME = "failed to get the Neo4j instance home folder"
    LOAD_SUCCESS = "successfully to load the data"
    LOAD_FAILED = "failed to load the data"
    STOP_FAILED = "failed to stop the instance to import the data"
    START_FAILED = "failed to restart the database after the import"
    RECOVERY_SUCCESS = "successfully recovery the database after the failed import"
    RECOVERY_FAILED = "failed to recovery the database"
