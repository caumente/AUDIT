# export PYTHONPATH=$PYTHONPATH:/home/usr/AUDIT/src
import pytest
import numpy as np
from scipy.stats import skew
from scipy.stats import kurtosis
from src.features.statistical import StatisticalFeatures


@pytest.fixture
def mock_sequence():
    """Fixture to create a mock 3D sequence array for testing statistical features."""
    return np.array([
        [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
        [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
    ])


@pytest.fixture
def mock_flat_sequence():
    """Fixture to create a mock flat 1D sequence array for testing edge cases."""
    return np.array([1, 2, 3, 4, 5])


def test_get_max_intensity(mock_sequence):
    """Test the calculation of the maximum intensity."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_max_intensity()
    assert result == 26, "Maximum intensity calculation is incorrect."


def test_get_min_intensity(mock_sequence):
    """Test the calculation of the minimum intensity."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_min_intensity()
    assert result == 0, "Minimum intensity calculation is incorrect."


def test_get_mean_intensity(mock_sequence):
    """Test the calculation of the mean intensity."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_mean_intensity()
    expected_mean = mock_sequence.mean()
    assert result == pytest.approx(expected_mean), "Mean intensity calculation is incorrect."


def test_get_median_intensity(mock_sequence):
    """Test the calculation of the median intensity."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_median_intensity()
    expected_median = np.median(mock_sequence)
    assert result == pytest.approx(expected_median), "Median intensity calculation is incorrect."


def test_get_std_intensity(mock_sequence):
    """Test the calculation of the standard deviation of intensity values."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_std_intensity()
    expected_std = mock_sequence.std()
    assert result == pytest.approx(expected_std), "Standard deviation calculation is incorrect."


def test_get_range_intensity(mock_sequence):
    """Test the calculation of the range of intensity values."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_range_intensity()
    expected_range = mock_sequence.max() - mock_sequence.min()
    assert result == expected_range, "Range intensity calculation is incorrect."


def test_get_skewness(mock_sequence):
    """Test the calculation of skewness."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_skewness()
    expected_skewness = skew(mock_sequence.flatten())
    assert result == pytest.approx(expected_skewness), "Skewness calculation is incorrect."


def test_get_kurtosis(mock_sequence):
    """Test the calculation of kurtosis."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.get_kurtosis()
    expected_kurtosis = kurtosis(mock_sequence.flatten())
    assert result == pytest.approx(expected_kurtosis), "Kurtosis calculation is incorrect."


def test_extract_features(mock_sequence):
    """Test the extraction of all statistical features."""
    stats_features = StatisticalFeatures(mock_sequence)
    result = stats_features.extract_features()

    expected_features = {
        "max_intensity": 26,
        "min_intensity": 0,
        "mean_intensity": mock_sequence.mean(),
        "median_intensity": np.median(mock_sequence),
        "10_perc_intensity": np.percentile(mock_sequence, 10),
        "90_perc_intensity": np.percentile(mock_sequence, 90),
        "std_intensity": mock_sequence.std(),
        "range_intensity": 26 - 0,
        "skewness": skew(mock_sequence.flatten()),
        "kurtosis": kurtosis(mock_sequence.flatten()),
    }
    for key, value in expected_features.items():
        assert result[key] == pytest.approx(value), f"{key} feature calculation is incorrect."


def test_get_percentile_n(mock_sequence):
    """Test the calculation of n-th percentile."""
    stats_features = StatisticalFeatures(mock_sequence)
    result_10 = stats_features.get_percentile_n(10)
    result_90 = stats_features.get_percentile_n(90)

    expected_10 = np.percentile(mock_sequence, 10)
    expected_90 = np.percentile(mock_sequence, 90)

    assert result_10 == pytest.approx(expected_10), "10th percentile calculation is incorrect."
    assert result_90 == pytest.approx(expected_90), "90th percentile calculation is incorrect."


def test_extract_features_flat_sequence(mock_flat_sequence):
    """Test the extraction of features with a flat 1D sequence."""
    stats_features = StatisticalFeatures(mock_flat_sequence)
    result = stats_features.extract_features()

    expected_features = {
        "max_intensity": 5,
        "min_intensity": 1,
        "mean_intensity": mock_flat_sequence.mean(),
        "median_intensity": np.median(mock_flat_sequence),
        "10_perc_intensity": np.percentile(mock_flat_sequence, 10),
        "90_perc_intensity": np.percentile(mock_flat_sequence, 90),
        "std_intensity": mock_flat_sequence.std(),
        "range_intensity": 5 - 1,
        "skewness": skew(mock_flat_sequence),
        "kurtosis": kurtosis(mock_flat_sequence),
    }
    for key, value in expected_features.items():
        assert result[key] == pytest.approx(value), f"{key} feature calculation is incorrect in flat sequence."
