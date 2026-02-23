from typing import Callable, Optional

import pandas as pd

from quality.types import QualityScore
from utils.utils import logger


def ratio(
    df: Optional[pd.DataFrame], func: Callable[[pd.DataFrame], int], total: int
) -> Optional[QualityScore]:
    """
    Compute a quality score based on the analysis of the database.

    :param df: DataFrame who contains the data.
    :type df: Optional[pd.DataFrame]
    :param func: Function to be applied on `df` who calculate the number of invalid values detected.
    :type func: Callable[[pd.DataFrame], int]
    :param total: The number who represent the population of the data.
    :type total: int
    :return: The quality score.
    :rtype: QualityScore | None
    """

    if df is None:
        return QualityScore(total, total)
    else:
        try:
            invalid: int | float = func(df)
            valid: int = int(total - invalid)
            return QualityScore(valid, total)
        except Exception as error:
            logger.error(error)
            return None
