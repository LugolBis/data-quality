import subprocess
from typing import Optional, TypeGuard, TypeVar

from loguru import logger

T = TypeVar("T")

# Configure the logger :
logger.add(
    "logs/extraction.log",
    rotation="1 MB",  # Automatic rotation after 1MB
    retention="7 days",  # Delete the files older than 7 days
    compression="zip",  # Compress the old logs files
    level="DEBUG",  # Minimal logs level
    format="[{time:YYYY-MM-DD HH:mm:ss}] [{file}:{line}] [{level}] : {message}",
)


def some(option: Optional[T]) -> TypeGuard[T]:
    """
    Provide a concise and safe way to to check the `option` took in input isn't a 'None' value.

    :param option: An optional value, which can be a `None` or an object of type `T`
    :type option: Optional[T]
    :return: A wrapped boolean who's bring the power of `mypy`
    :rtype: TypeGuard[T]
    """
    return option is not None


def safe_exec(command: list[str]) -> bool:
    """
    Provide a safe way to execute a terminal command.

    :param command: The shell command to be executed.
    :type command: list[str]
    :return: If the command was successfully executed.
    :rtype: bool
    """

    try:
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            command, capture_output=True
        )

        if result != 0:
            logger.error(result.stderr)
        else:
            return True
    except Exception as error:
        logger.error(error)

    return False
