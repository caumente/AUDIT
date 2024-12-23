import numpy as np
import pandas as pd
import pytest

from src.metrics.commons import calculate_absolute_error
from src.metrics.commons import calculate_improvements
from src.metrics.commons import calculate_ratio_improvement
from src.metrics.commons import calculate_relative_error


@pytest.fixture
def valid_data():
    return pd.DataFrame({"init": [10, 0, 5], "end": [15, 0, 10]})


@pytest.fixture
def data_with_missing_column():
    return pd.DataFrame({"init": [10, 20, 30]})


@pytest.fixture
def data_empty():
    return pd.DataFrame({"init": [], "end": []})


def test_calculate_relative_error(valid_data):
    result = calculate_relative_error(valid_data, "init", "end")
    expected = pd.Series([50.0, np.nan, 100.0])  # Division by zero leads to NaN
    pd.testing.assert_series_equal(result, expected, check_dtype=False)


def test_calculate_absolute_error(valid_data):
    result = calculate_absolute_error(valid_data, "init", "end")
    expected = pd.Series([5, 0, 5])
    pd.testing.assert_series_equal(result, expected)


def test_calculate_ratio_improvement(valid_data):
    result = calculate_ratio_improvement(valid_data, "init", "end")
    expected = pd.Series([1.5, np.nan, 2.0])  # Division by zero leads to NaN
    pd.testing.assert_series_equal(result, expected, check_dtype=False)


def test_calculate_improvements(valid_data):
    result = calculate_improvements(valid_data.copy(), "init", "end")
    expected = valid_data.copy()
    expected["relative"] = pd.Series([50.0, np.nan, 100.0])
    expected["absolute"] = pd.Series([5, 0, 5])
    expected["ratio"] = pd.Series([1.5, np.nan, 2.0])
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_improvements_partial(valid_data):
    result = calculate_improvements(valid_data.copy(), "init", "end", values=["absolute"])
    expected = valid_data.copy()
    expected["absolute"] = pd.Series([5, 0, 5])
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_improvements_missing_columns(data_with_missing_column):
    with pytest.raises(ValueError, match="Columns 'init' and 'end' must exist in the DataFrame."):
        calculate_improvements(data_with_missing_column, "init", "end")


def test_calculate_improvements_empty_dataframe(data_empty):
    result = calculate_improvements(data_empty.copy(), "init", "end")
    expected = pd.DataFrame({"init": [], "end": [], "relative": [], "absolute": [], "ratio": []})
    pd.testing.assert_frame_equal(result, expected)
