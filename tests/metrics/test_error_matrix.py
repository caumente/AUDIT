import numpy as np
import pytest

from src.metrics.error_matrix import errors_per_class
from src.metrics.error_matrix import normalize_matrix_per_row


# Test data for errors_per_class function
@pytest.fixture
def simple_data():
    ground_truth = [0, 1, 0, 2, 1, 2, 0, 1]
    predicted = [0, 0, 0, 2, 1, 1, 0, 2]
    unique_classes = [0, 1, 2]
    return ground_truth, predicted, unique_classes


@pytest.fixture
def edge_case_data():
    ground_truth = [0, 1, 1, 0, 2]
    predicted = [0, 1, 1, 0, 1]
    unique_classes = [0, 1, 2]
    return ground_truth, predicted, unique_classes


# Test errors_per_class function
def test_errors_per_class(simple_data):
    ground_truth, predicted, unique_classes = simple_data
    result = errors_per_class(ground_truth, predicted, unique_classes)

    expected = np.array(
        [
            [0, 0, 0],  # Class 0 was predicted 2 times (correctly) for ground truth 0
            [1, 0, 1],  # Class 1 was predicted 1 time (correctly) for ground truth 1
            [0, 1, 0],
        ]
    )  # Class 2 was predicted 1 time (correctly) for ground truth 2
    # Check if the result matches expected
    np.testing.assert_array_equal(result, expected)


def test_errors_per_class_edge_case(edge_case_data):
    ground_truth, predicted, unique_classes = edge_case_data
    result = errors_per_class(ground_truth, predicted, unique_classes)

    expected = np.array(
        [
            [0, 0, 0],  # Class 0 was predicted 1 time (correctly) for ground truth 0
            [0, 0, 0],  # Class 1 was predicted 2 times (correctly) for ground truth 1
            [0, 1, 0],
        ]
    )  # Class 2 was predicted 0 times for ground truth 2
    # Check if the result matches expected
    np.testing.assert_array_equal(result, expected)


# Test normalize_matrix_per_row function
def test_normalize_matrix_per_row():
    matrix = np.array([[1, 4, 5], [2, 8, 10], [4, 5, 1]])
    result = normalize_matrix_per_row(matrix)

    expected = np.array(
        [
            [10.0, 40.0, 50.0],  # First row is normalized to 100
            [10.0, 40.0, 50.0],  # Second row normalized to 100
            [40.0, 50.0, 10.0],
        ]
    )  # Third row normalized to 100

    np.testing.assert_equal(result, expected)


def test_normalize_matrix_per_row_zero_sum():
    matrix = np.array([[0, 0, 0], [0, 0, 0], [1, 1, 1]])
    result = normalize_matrix_per_row(matrix)

    # In this case, the rows that sum to 0 should be replaced with 0s
    expected = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [33.33333333, 33.33333333, 33.33333333]])

    np.testing.assert_almost_equal(result, expected, decimal=6)


def test_normalize_matrix_per_row_empty():
    matrix = np.array([[], [], []])
    result = normalize_matrix_per_row(matrix)

    # An empty matrix should return an empty matrix
    np.testing.assert_array_equal(result, matrix)
