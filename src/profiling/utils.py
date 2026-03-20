from math import nan, sqrt

from profiling.types import Statistics


def _compute_statistics(data: list[int | float]) -> Statistics | None:
    if len(data) < 1:
        return None
    sorted_data = sorted(data)
    n = len(sorted_data)

    count = n
    limits = (sorted_data[0], sorted_data[-1])
    sum_ = sum(sorted_data)
    average = sum(sorted_data) / n

    # Variance (population)
    variance = sum((x - average) ** 2 for x in sorted_data) / n
    standard_deviation = sqrt(variance)

    # Median (Q2)
    median = _compute_median(sorted_data)
    q2 = median

    # Quartiles (median of halves method, not including the median if n odd)
    if n % 2 == 0:
        lower_half = sorted_data[: n // 2]
        upper_half = sorted_data[n // 2 :]
    else:
        lower_half = sorted_data[: n // 2]
        upper_half = sorted_data[n // 2 + 1 :]

    q1 = _compute_median(lower_half)
    q3 = _compute_median(upper_half)

    return Statistics(
        count,
        limits,
        sum_,
        average,
        median,
        variance,
        standard_deviation,
        q1,
        q2,
        q3,
    )


def _compute_median(sorted_values: list[int | float]) -> float:
    try:
        m = len(sorted_values)
        mid = m // 2
        if m % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2
        return sorted_values[mid]
    except IndexError:
        return nan
