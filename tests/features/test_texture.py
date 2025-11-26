import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import numpy as np
import pytest

from src.audit.features.texture import TextureFeatures


@pytest.fixture
def mock_sequence():
    """Fixture to create a mock 3D sequence array for testing texture features."""
    return np.array(
        [
            [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            [[9, 10, 11], [12, 13, 14], [15, 16, 17]],
            [[18, 19, 20], [21, 22, 23], [24, 25, 26]],
        ]
    )


@pytest.fixture
def mock_zero_sequence():
    """Fixture to create a mock 3D sequence array with all values defined to 0 for testing texture features."""
    return np.array(
        [
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
    )


@pytest.fixture
def mock_sequence_with_empty_planes():
    """Fixture to create a mock 3D sequence array with some empty planes."""
    return np.array(
        [
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 10, 11], [12, 13, 14], [15, 16, 0]],
            [[0, 0, 0], [12, 13, 14], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
    )


def test_compute_texture_values(mock_sequence):
    """Test the calculation of texture values."""
    texture_features = TextureFeatures(mock_sequence)
    result = texture_features.compute_texture_values("contrast")

    assert len(result) == mock_sequence.shape[0], "The number of texture values should match the number of planes."
    assert isinstance(result, np.ndarray), "Result should be a numpy array."
    assert np.all(np.isfinite(result)), "All computed texture values should be finite."


def test_compute_texture_values_zero_sequence(mock_zero_sequence):
    """Test the calculation of texture values with an empty sequence."""
    texture_features = TextureFeatures(mock_zero_sequence)
    result = texture_features.compute_texture_values("contrast")

    # Check that the result is NaN because all values in the sequence are zero
    assert np.isnan(result), "The texture value should be NaN for a sequence of all zeros."


def test_compute_texture_values_with_empty_planes(mock_sequence_with_empty_planes):
    """Test if empty planes are handled correctly when remove_empty_planes is True."""
    texture_features = TextureFeatures(mock_sequence_with_empty_planes, remove_empty_planes=True)

    # Perform texture value computation for 'contrast'
    result = texture_features.compute_texture_values("contrast")

    # After removing empty planes, the number of planes should be 1 (the middle plane)
    assert len(result) == 4, "There should be 1 texture value after removing empty planes."

    # # The result should be a numpy array
    assert isinstance(result, np.ndarray), "Result should be a numpy array."

    # # Ensure that all computed texture values are finite (not NaN or Inf)
    assert np.all(np.isfinite(result)), "All computed texture values should be finite."


def test_extract_features_valid_sequence(mock_sequence):
    """Test extraction of features from a valid sequence with multiple textures."""
    texture_features = TextureFeatures(mock_sequence)
    textures = ["contrast", "dissimilarity", "homogeneity", "ASM", "energy", "correlation"]

    # Extract features
    result = texture_features.extract_features(textures=textures)

    # Assert that the result is a dictionary
    assert isinstance(result, dict), "The result should be a dictionary."

    # Assert that the expected texture features are present in the dictionary
    for texture in textures:
        assert f"mean_{texture}" in result, f"Missing mean for texture {texture}."
        assert f"std_{texture}" in result, f"Missing standard deviation for texture {texture}."

    # Check that the features contain numerical values (no NaNs or infinities)
    for key, value in result.items():
        assert np.isfinite(value), f"Feature {key} contains non-finite values."


def test_extract_features_zero_sequence(mock_zero_sequence):
    """Test extraction of features from a sequence with all zero values."""
    texture_features = TextureFeatures(mock_zero_sequence)
    textures = ["contrast", "dissimilarity", "homogeneity", "ASM", "energy", "correlation"]

    # Extract features
    result = texture_features.extract_features(textures=textures)

    # Assert that the results contain NaN for all features in a zero-sequence
    for texture in textures:
        mean_key = f"mean_{texture}"
        std_key = f"std_{texture}"

        # Check that the mean and std are NaN for each texture
        assert np.isnan(result[mean_key]), f"{mean_key} should be NaN for all-zero sequence."
        assert np.isnan(result[std_key]), f"{std_key} should be NaN for all-zero sequence."


def test_extract_features_with_empty_planes(mock_sequence_with_empty_planes):
    """Test extraction of features from a sequence with some empty planes."""
    texture_features = TextureFeatures(mock_sequence_with_empty_planes, remove_empty_planes=True)
    textures = ["contrast", "dissimilarity", "homogeneity", "ASM", "energy", "correlation"]

    # Extract features
    result = texture_features.extract_features(textures=textures)

    # Assert that the results contain numerical values (no NaNs or infinities) after removing empty planes
    for texture in textures:
        mean_key = f"mean_{texture}"
        std_key = f"std_{texture}"

        assert mean_key in result, f"Missing {mean_key} in the result."
        assert std_key in result, f"Missing {std_key} in the result."
        assert np.isfinite(result[mean_key]), f"{mean_key} should be a finite value."
        assert np.isfinite(result[std_key]), f"{std_key} should be a finite value."


def test_extract_features_with_default_textures(mock_sequence):
    """Test extraction of features with the default list of textures."""
    texture_features = TextureFeatures(mock_sequence)

    # Extract features with default textures
    result = texture_features.extract_features()

    # Assert that the result is a dictionary
    assert isinstance(result, dict), "The result should be a dictionary."

    # Assert that the expected default texture features are present in the dictionary
    default_textures = ["contrast", "dissimilarity", "homogeneity", "ASM", "energy", "correlation"]
    for texture in default_textures:
        assert f"mean_{texture}" in result, f"Missing mean for texture {texture}."
        assert f"std_{texture}" in result, f"Missing standard deviation for texture {texture}."

    # Check that the features contain numerical values (no NaNs or infinities)
    for key, value in result.items():
        assert np.isfinite(value), f"Feature {key} contains non-finite values."


def test_extract_single_texture(mock_sequence):
    """Test extraction of features for a single texture."""
    texture_features = TextureFeatures(mock_sequence)

    # Extract features for just the 'contrast' texture
    result = texture_features.extract_features(textures=["contrast"])

    # Assert that the result is a dictionary
    assert isinstance(result, dict), "The result should be a dictionary."
    assert "mean_contrast" in result, "Missing mean for contrast."
    assert "std_contrast" in result, "Missing standard deviation for contrast."

    # Check that the features contain numerical values (no NaNs or infinities)
    for key, value in result.items():
        assert np.isfinite(value), f"Feature {key} contains non-finite values."


def test_compute_texture_values_no_removal(mock_sequence_with_empty_planes):
    """Test if texture values are computed without removing empty planes."""
    texture_features = TextureFeatures(mock_sequence_with_empty_planes, remove_empty_planes=False)

    # Perform texture value computation for 'contrast'
    result = texture_features.compute_texture_values("contrast")

    # The number of planes should match the original sequence (5 planes in this case)
    assert (
        len(result) == mock_sequence_with_empty_planes.shape[0]
    ), "The number of texture values should match the number of planes."

    # Ensure that all computed texture values are finite
    assert np.all(np.isfinite(result)), "All computed texture values should be finite."
