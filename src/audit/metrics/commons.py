import numpy as np


def calculate_relative_error(data, init, end):
    """
    Calculate the relative error between two columns in a DataFrame.

    Parameters:
    - data: DataFrame containing the data.
    - init: Initial column name.
    - end: Ending column name.

    Returns:
    - relative_error: Series containing the relative error.
    """
    return 100 * (data[end] - data[init]) / data[init]


def calculate_absolute_error(data, init, end):
    """
    Calculate the absolute error between two columns in a DataFrame.

    Parameters:
    - data: DataFrame containing the data.
    - init: Initial column name.
    - end: Ending column name.

    Returns:
    - absolute_error: Series containing the relative error.
    """
    return data[end] - data[init]


def calculate_ratio_improvement(data, init, end):
    """
    Calculate the ratio of improvement between two columns in a DataFrame.

    Parameters:
    - data: DataFrame containing the data.
    - init: Initial column name.
    - end: Ending column name.

    Returns:
    - ratio_improvement: Series containing the relative error.
    """

    return (data[end]) / (data[init])


def calculate_improvements(data, init, end, values=None):
    if values is None:
        values = ['relative', 'absolute', 'ratio']

    if init not in data or end not in data:
        raise ValueError(f"Columns '{init}' and '{end}' must exist in the DataFrame.")

    if 'relative' in values:
        data["relative"] = calculate_relative_error(data, init, end)
    if 'absolute' in values:
        data["absolute"] = calculate_absolute_error(data, init, end)
    if 'ratio' in values:
        data["ratio"] = calculate_ratio_improvement(data, init, end)

    return data.replace([np.inf, -np.inf], np.nan)
