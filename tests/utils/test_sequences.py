from unittest import mock

import numpy as np
import pytest
import SimpleITK as sitk

from src.utils.sequences import build_nifty_image
from src.utils.sequences import fit_brain_boundaries
from src.utils.sequences import get_spacing
from src.utils.sequences import label_replacement
from src.utils.sequences import load_nii
from src.utils.sequences import read_sequences_dict

# Mock NIfTI Image
mock_nii_image = mock.Mock()
mock_nii_image.GetArrayFromImage.return_value = np.zeros((10, 10, 10))  # Simulate an image data as a numpy array
mock_nii_image.GetSpacing.return_value = (2.0, 2.0, 2.0)  # Mock spacing returned by GetSpacing


@pytest.fixture
def dummy_sequence_path():
    return "./tests/dummy_sequence.nii.gz"


@pytest.fixture
def fake_sequence_path():
    return "./tests/fake_sequence.nii.gz"


# Fixtures for reusable test inputs
@pytest.fixture
def sample_segmentation():
    """
    A small sample segmentation array for testing.
    """
    return np.array([[0, 1, 2], [3, 0, 1], [2, 3, 0]])


@pytest.fixture
def original_labels():
    """
    A list of original labels present in the sample segmentation array.
    """
    return [0, 1, 2, 3]


@pytest.fixture
def new_labels():
    """
    A list of new labels to replace the original labels.
    """
    return [10, 11, 12, 13]


def test_load_nii_valid_file(dummy_sequence_path):
    result = load_nii(dummy_sequence_path, as_array=False)
    assert isinstance(result, sitk.Image), "The result should be a SimpleITK Image"

    result_array = load_nii(dummy_sequence_path, as_array=True)
    assert isinstance(result_array, np.ndarray), "The result should be a numpy array"


def test_load_nii_invalid_path(fake_sequence_path):
    with pytest.raises(ValueError, match="does not exist or is not a valid file"):
        load_nii(fake_sequence_path, as_array=False)


def test_load_nii_empty_path():
    with pytest.raises(ValueError, match="does not exist or is not a valid file"):
        load_nii("", as_array=False)


def test_load_nii_none_path():
    with pytest.raises(ValueError, match="does not exist or is not a valid file"):
        load_nii(None, as_array=False)


def test_read_sequences_dict_valid():
    root = "/mock/path"
    subject_id = "subject_1"
    sequences = ["_t1", "_t1ce"]

    # Mock os.path.isfile to return True for the sequences
    with mock.patch("os.path.isfile") as mock_isfile, mock.patch(
        "src.utils.sequences.load_nii", return_value=mock_nii_image
    ):
        mock_isfile.side_effect = lambda x: x.endswith("_t1.nii.gz") or x.endswith("_t1ce.nii.gz")

        result = read_sequences_dict(root, subject_id, sequences)

    assert result["t1"] == mock_nii_image
    assert result["t1ce"] == mock_nii_image


def test_read_sequences_dict_with_missing_sequences():
    root = "/mock/path"
    subject_id = "subject_1"
    sequences = ["_t1", "_t2", "_flair"]

    # Mock os.path.isfile to simulate file existence
    with mock.patch("os.path.isfile") as mock_isfile, mock.patch("src.utils.sequences.load_nii") as mock_load_nii:
        # Only mock _t1 as existing
        mock_isfile.side_effect = lambda x: x == "/mock/path/subject_1/subject_1_t1.nii.gz"
        mock_load_nii.return_value = mock_nii_image

        result = read_sequences_dict(root, subject_id, sequences)

    # Validate the expected result: _t1 exists and others are None
    assert result["t1"] == mock_nii_image
    assert result["t2"] is None
    assert result["flair"] is None


def test_read_sequences_dict_invalid_parameters():
    with pytest.raises(ValueError, match="Both 'root path' and 'subject id' must be non-empty strings."):
        read_sequences_dict("", "subject_1")  # Empty root

    with pytest.raises(ValueError, match="Both 'root path' and 'subject id' must be non-empty strings."):
        read_sequences_dict("/mock/path", "")  # Empty subject_id


def test_read_sequences_dict_with_load_nii_error():
    root = "/mock/path"
    subject_id = "subject_1"
    sequences = ["_t1", "_t1ce"]

    # Mock os.path.isfile to simulate file existence
    with mock.patch("os.path.isfile") as mock_isfile, mock.patch(
        "src.utils.sequences.load_nii", side_effect=RuntimeError("NIfTI load error")
    ):
        mock_isfile.side_effect = lambda x: x.endswith("_t1.nii.gz") or x.endswith("_t1ce.nii.gz")

        result = read_sequences_dict(root, subject_id, sequences)

    # Both sequences should be None due to load_nii error
    assert result["t1"] is None
    assert result["t1ce"] is None


def test_read_sequences_dict_files_missing():
    root = "/mock/path"
    subject_id = "subject_1"
    sequences = ["_t1", "_t1ce"]

    # Mock os.path.isfile to simulate that the files do not exist
    with mock.patch("os.path.isfile") as mock_isfile:
        mock_isfile.side_effect = lambda x: False  # Simulate that no file exists

        result = read_sequences_dict(root, subject_id, sequences)

    # All sequences should be None as files are missing
    assert result["t1"] is None
    assert result["t1ce"] is None


def test_get_spacing_with_image():
    # Call get_spacing with the mock image
    spacing = get_spacing(mock_nii_image)

    # Assert the correct spacing was returned
    np.testing.assert_array_equal(spacing, np.array([2.0, 2.0, 2.0]))


def test_get_spacing_with_none_image():
    # Mock the logger to capture the warning
    with mock.patch("src.utils.sequences.logger.warning") as mock_warning:
        spacing = get_spacing(None)

        # Assert that the spacing returned is the default [1, 1, 1]
        np.testing.assert_array_equal(spacing, np.array([1, 1, 1]))

        # Verify the warning was logged
        mock_warning.assert_called_once_with("Sequence empty. Assuming isotropic spacing (1, 1, 1).")


def test_get_spacing_with_valid_sequence(dummy_sequence_path):
    # Mock load_nii to simulate loading a valid image and returning the mock image
    with mock.patch("src.utils.sequences.load_nii", return_value=mock_nii_image):
        # Simulate that the file exists (by mocking os.path.isfile)
        with mock.patch("os.path.isfile", return_value=True):
            img = load_nii(dummy_sequence_path)  # This will use the mocked image

            # Call get_spacing with the loaded image
            spacing = get_spacing(img)

            # Assert the correct spacing was returned
            np.testing.assert_array_equal(spacing, np.array([1.0, 1.0, 1.0]))


# Test with valid segmentation array
def test_build_nifty_image_valid_input():
    segmentation = np.zeros((10, 10, 10), dtype=np.uint8)  # Example valid segmentation array

    # Call the function
    nifty_img = build_nifty_image(segmentation)

    # Assert that the output is a SimpleITK Image
    assert isinstance(nifty_img, sitk.Image)


def test_build_nifty_image_invalid_input():
    invalid_input = "not an array"

    # Assert that a ValueError is raised for invalid input
    with pytest.raises(ValueError, match="The segmentation input must be a Numpy array or array-like object."):
        build_nifty_image(invalid_input)


def test_build_nifty_image_array_like_input():
    array_like_input = [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]  # A nested list, array-like structure

    # Call the function
    nifty_img = build_nifty_image(array_like_input)

    # Assert that the output is a SimpleITK Image
    assert isinstance(nifty_img, sitk.Image)


def test_label_replacement_basic(sample_segmentation, original_labels, new_labels):
    """
    Test the basic functionality of label_replacement.
    """
    expected_output = np.array([[10, 11, 12], [13, 10, 11], [12, 13, 10]])

    output = label_replacement(sample_segmentation, original_labels, new_labels)
    assert np.array_equal(output, expected_output), f"Expected {expected_output}, but got {output}"


def test_label_replacement_partial_labels(sample_segmentation):
    """
    Test with partial label mapping (some labels remain unchanged).
    """
    original_labels = [1, 2]  # Only replace labels 1 and 2
    new_labels = [101, 102]

    expected_output = np.array([[0, 101, 102], [3, 0, 101], [102, 3, 0]])

    output = label_replacement(sample_segmentation, original_labels, new_labels)
    assert np.array_equal(output, expected_output), f"Expected {expected_output}, but got {output}"


def test_label_replacement_no_mapping(sample_segmentation):
    """
    Test with empty original and new labels (no changes should be made).
    """
    original_labels = []
    new_labels = []

    expected_output = np.copy(sample_segmentation)

    output = label_replacement(sample_segmentation, original_labels, new_labels)
    assert np.array_equal(output, expected_output), f"Expected {expected_output}, but got {output}"


def test_label_replacement_invalid_input_lengths(sample_segmentation):
    """
    Test with mismatched lengths of original_labels and new_labels.
    """
    original_labels = [0, 1]  # Only two original labels
    new_labels = [10]  # Only one new label

    with pytest.raises(ValueError, match="The lengths of original labels and new labels must match."):
        label_replacement(sample_segmentation, original_labels, new_labels)


def test_label_replacement_no_changes(sample_segmentation):
    """
    Test where new_labels matches original_labels (no changes should occur).
    """
    original_labels = [0, 1, 2, 3]
    new_labels = [0, 1, 2, 3]  # Same as original

    expected_output = np.copy(sample_segmentation)

    output = label_replacement(sample_segmentation, original_labels, new_labels)
    assert np.array_equal(output, expected_output), f"Expected {expected_output}, but got {output}"


def test_fit_brain_boundaries_with_padding():
    # Create a sequence with non-zero values and padding
    sequence = np.zeros((10, 10, 10))
    sequence[2:8, 2:8, 2:8] = 1  # Non-zero values in the middle

    # Call fit_brain_boundaries with padding = 1
    result = fit_brain_boundaries(sequence, padding=1)

    assert result.shape == (8, 8, 8), "Shape mismatch after fitting with padding."


def test_fit_brain_boundaries_all_non_zero_values():
    # Create a sequence with all non-zero values
    sequence = np.ones((10, 10, 10))

    # Call fit_brain_boundaries with padding = 1
    result = fit_brain_boundaries(sequence, padding=1)

    # Expected output: since the entire array is non-zero, it should remain the same size with padding
    assert result.shape == (10, 10, 10), "Shape mismatch for all non-zero sequence."


def test_fit_brain_boundaries_padding_exceeds_boundary():
    # Create a sequence with non-zero values near the edge
    sequence = np.zeros((10, 10, 10))
    sequence[8:, 8:, 8:] = 1  # Non-zero values in the corner

    # Call fit_brain_boundaries with padding that exceeds array size
    result = fit_brain_boundaries(sequence, padding=2)

    assert result.shape == (4, 4, 4), "Shape mismatch after padding exceeds boundary."


def test_fit_brain_boundaries_zero_padding():
    # Create a sequence with non-zero values and zero padding
    sequence = np.zeros((10, 10, 10))
    sequence[2:8, 2:8, 2:8] = 1  # Non-zero values in the middle

    # Call fit_brain_boundaries with padding = 0 (no padding)
    result = fit_brain_boundaries(sequence, padding=0)

    assert result.shape == (6, 6, 6), "Shape mismatch after fitting with zero padding."
