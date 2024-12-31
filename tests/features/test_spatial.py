import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
import pytest

from src.audit.features.spatial import SpatialFeatures


@pytest.fixture
def mock_sequence():
    """Fixture to create a 5x5x5 mock sequence array with boundaries set to 0 and inside voxels set to 1."""
    sequence = np.zeros((5, 5, 5), dtype=int)
    sequence[1:4, 1:4, 1:4] = 1
    return sequence


@pytest.fixture
def mock_isotropic_spacing():
    """Fixture to create a mock spacing array."""
    return np.array([1.0, 1.0, 1.0])


@pytest.fixture
def mock_non_isotropic_spacing():
    """Fixture for non-isotropic voxel spacing."""
    return np.array([2.0, 0.5, 2.0])


def test_calculate_brain_center_mass(mock_sequence, mock_isotropic_spacing):
    """Test the calculation of brain center of mass with isotropic spacing."""
    spatial_features = SpatialFeatures(mock_sequence, mock_isotropic_spacing)
    result = spatial_features.calculate_brain_center_mass()

    expected_result = {
        "axial_brain_centre_mass": 2.0,
        "coronal_brain_centre_mass": 2.0,
        "sagittal_brain_centre_mass": 2.0,
    }
    assert result == pytest.approx(expected_result), "Center of mass calculation is incorrect with isotropic spacing."


def test_calculate_brain_center_mass_non_isotropic_spacing(mock_sequence, mock_non_isotropic_spacing):
    """Test the calculation of brain center of mass with non-isotropic spacing."""
    spatial_features = SpatialFeatures(mock_sequence, mock_non_isotropic_spacing)
    result = spatial_features.calculate_brain_center_mass()

    # Expected center of mass, scaled by non-isotropic spacing
    expected_result = {
        "axial_brain_centre_mass": 2.0 * 2.0,  # Axial spacing is 2.0
        "coronal_brain_centre_mass": 2.0 * 0.5,  # Coronal spacing is 0.5
        "sagittal_brain_centre_mass": 2.0 * 2.0,  # Sagittal spacing is 2.0
    }
    assert result == pytest.approx(
        expected_result
    ), "Center of mass calculation is incorrect with non-isotropic spacing."


def test_calculate_brain_center_mass_no_sequence():
    """Test the calculation of brain center of mass when sequence is None."""
    spatial_features = SpatialFeatures(None)
    result = spatial_features.calculate_brain_center_mass()

    expected_result = {
        "axial_brain_centre_mass": np.nan,
        "coronal_brain_centre_mass": np.nan,
        "sagittal_brain_centre_mass": np.nan,
    }
    assert result == expected_result, "Center of mass calculation should return NaNs for None sequence."


def test_get_shape(mock_sequence):
    """Test the shape extraction."""
    spatial_features = SpatialFeatures(mock_sequence)
    result = spatial_features.get_shape()

    expected_result = {
        "axial_dim": 5,
        "coronal_dim": 5,
        "sagittal_dim": 5,
    }
    assert result == expected_result, "Shape calculation is incorrect."


def test_get_dimensions_no_sequence():
    """Test the dimensions extraction when sequence is None."""
    spatial_features = SpatialFeatures(None)
    result = spatial_features.get_shape()

    expected_result = {
        "axial_dim": np.nan,
        "coronal_dim": np.nan,
        "sagittal_dim": np.nan,
    }
    assert result == expected_result, "Dimensions should return NaNs for None sequence."


def test_extract_features(mock_sequence, mock_isotropic_spacing):
    """Test the feature extraction method with isotropic spacing."""
    spatial_features = SpatialFeatures(mock_sequence, mock_isotropic_spacing)
    result = spatial_features.extract_features()

    expected_result = {
        "axial_dim": 5,
        "coronal_dim": 5,
        "sagittal_dim": 5,
        "axial_brain_centre_mass": 2.0,
        "coronal_brain_centre_mass": 2.0,
        "sagittal_brain_centre_mass": 2.0,
    }
    assert result == pytest.approx(expected_result), "Extracted features are incorrect with isotropic spacing."


def test_extract_features_no_sequence():
    """Test the feature extraction method with isotropic spacing."""
    spatial_features = SpatialFeatures(None, None)
    result = spatial_features.extract_features()

    expected_result = {
        "axial_dim": np.nan,
        "coronal_dim": np.nan,
        "sagittal_dim": np.nan,
        "axial_brain_centre_mass": np.nan,
        "coronal_brain_centre_mass": np.nan,
        "sagittal_brain_centre_mass": np.nan,
    }
    assert result == expected_result, "Extracted features are incorrect without sequence"
