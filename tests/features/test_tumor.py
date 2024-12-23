# export PYTHONPATH=$PYTHONPATH:/home/usr/AUDIT/src
import numpy as np
import pytest

from src.features.tumor import TumorFeatures


@pytest.fixture
def mock_segmentation():
    """Fixture to create a mock 3D segmentation array for testing tumor features."""
    return np.array([
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 1, 1]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    ])


@pytest.fixture
def mock_segmentation_multiple_labels():
    """Fixture to create a mock 3D segmentation array with multiple labels."""
    return np.array([
        [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[1, 2, 2], [2, 2, 0], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    ])


@pytest.fixture
def mock_zero_segmentation():
    """Fixture to create a mock 3D sequence array with all values defined to 0 for testing texture features."""
    return np.array([
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    ])


@pytest.fixture
def segmentation_with_float_labels():
    return np.array([
        [0.0, 1.0, 1.0],
        [2.0, 2.0, 0.0],
        [0.0, 0.0, 0.0]
    ])


@pytest.fixture
def brain_center_mass():
    """Fixture to provide a mock brain center mass for distance calculation."""
    return [1, 1, 1]


def test_count_tumor_pixels(mock_segmentation):
    """Test counting tumor pixels in the segmentation."""
    tumor_features = TumorFeatures(mock_segmentation)
    result = tumor_features.count_tumor_pixels()

    # Check that the result is a dictionary
    assert isinstance(result, dict), "Result should be a dictionary."
    assert 0 in result, "Tumor pixels should be counted for label 0."
    assert 1 in result, "Tumor pixels should be counted for label 1."
    assert result.get(0) == 22, "There should be 22 non-tumor pixels for label."
    assert result.get(1) == 5, "There should be 5 tumor pixels for label '1'."


def test_count_tumor_pixels_no_segmentation():
    """Test when the segmentation is None."""
    tumor_features = TumorFeatures(segmentation=None, mapping_names={"1": "Tumor", "2": "Edema"})
    result = tumor_features.count_tumor_pixels()

    # Check that the result contains NaN values for the provided mapping names
    assert result == {"tumor": np.nan, "edema": np.nan}, "Result should contain NaN for all mapped names."


def test_count_tumor_pixels_no_segmentation_no_mapping():
    """Test when segmentation is None and no mapping names are provided."""
    tumor_features = TumorFeatures(segmentation=None, mapping_names=None)
    result = tumor_features.count_tumor_pixels()

    # Check that the result is an empty dictionary
    assert result == {}, "Result should be an empty dictionary when no mapping is provided."


def test_count_tumor_pixels_basic_segmentation(mock_segmentation):
    """Test counting tumor pixels in a basic segmentation."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation)
    result = tumor_features.count_tumor_pixels()

    # Check that the result matches expected pixel counts
    assert result == {0: 22, 1: 5}, "Result should match the expected pixel counts."


def test_count_tumor_pixels_with_mapping(mock_segmentation_multiple_labels):
    """Test counting tumor pixels with mapping names provided."""
    mapping_names = {1: "Tumor", 2: "Edema", 0: "bkg"}
    tumor_features = TumorFeatures(segmentation=mock_segmentation_multiple_labels, mapping_names=mapping_names)
    result = tumor_features.count_tumor_pixels()

    # Check that the result uses the mapped names and counts are correct
    assert result == {"bkg": 21, "tumor": 2, "edema": 4}, "Result should match the expected pixel counts with mapping."


def test_count_tumor_pixels_with_partial_mapping(mock_segmentation_multiple_labels):
    """Test counting tumor pixels when only partial mapping names are provided."""
    mapping_names = {1: "Tumor", 0: "Background"}
    tumor_features = TumorFeatures(segmentation=mock_segmentation_multiple_labels, mapping_names=mapping_names)
    result = tumor_features.count_tumor_pixels()

    # Check that the unmapped label retains its original value
    assert result == {"background": 21, "tumor": 2, "2": 4}, "Result should retain unmapped labels and map others correctly."


def test_count_tumor_pixels_empty_segmentation():
    """Test counting tumor pixels in an empty segmentation array."""
    empty_segmentation = np.array([])
    tumor_features = TumorFeatures(segmentation=empty_segmentation)
    result = tumor_features.count_tumor_pixels()

    # Check that the result is an empty dictionary
    assert result == {}, "Result should be an empty dictionary for an empty segmentation."


def test_count_tumor_pixels_with_only_background(mock_zero_segmentation):
    """Test counting tumor pixels in a segmentation with only background values."""
    tumor_features = TumorFeatures(segmentation=mock_zero_segmentation, mapping_names={0: "Background"})
    result = tumor_features.count_tumor_pixels()

    # Check that only the background is counted
    assert result == {"background": 27}, "Result should count only background pixels."


def test_count_tumor_pixels_with_negative_values():
    """Test counting tumor pixels in a segmentation with negative values."""
    segmentation_with_negative_values = np.array([
        [0, -1, -1],
        [1, 1, 0],
        [0, 0, 0]
    ])
    mapping_names = {-1: "Artifact", 1: "Tumor", 0: "Background"}
    tumor_features = TumorFeatures(segmentation=segmentation_with_negative_values, mapping_names=mapping_names)
    result = tumor_features.count_tumor_pixels()

    # Check that negative values are correctly counted and mapped
    assert result == {"background": 5, "artifact": 2, "tumor": 2}, "Result should correctly count and map negative values."


def test_count_tumor_pixels_non_integer_labels(segmentation_with_float_labels):
    """Test counting tumor pixels in a segmentation with non-integer labels."""
    mapping_names = {0.0: "Background", 1.0: "Tumor1", 2.0: "Tumor2"}
    tumor_features = TumorFeatures(segmentation=segmentation_with_float_labels, mapping_names=mapping_names)
    result = tumor_features.count_tumor_pixels()

    # Check that floating-point labels are correctly counted and mapped
    assert result == {"background": 5, "tumor1": 2, "tumor2": 2}, "Result should correctly count and map float labels."


def test_calculate_lesion_size_no_segmentation():
    """Test when segmentation is None."""
    tumor_features = TumorFeatures(segmentation=None)
    result = tumor_features.calculate_lesion_size()

    # Check that the result contains NaN
    assert result == {"lesion_size": np.nan}, "Result should be NaN when segmentation is None."


def test_calculate_lesion_size_empty_segmentation():
    """Test when segmentation is an empty array."""
    empty_segmentation = np.array([])
    tumor_features = TumorFeatures(segmentation=empty_segmentation)
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size is zero for an empty array
    assert result == {"lesion_size": 0}, "Result should be 0 for an empty segmentation."


def test_calculate_lesion_size_all_zero_segmentation(mock_zero_segmentation):
    """Test when segmentation contains only zeros."""
    tumor_features = TumorFeatures(segmentation=mock_zero_segmentation)
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size is zero for an all-zero segmentation
    assert result == {"lesion_size": 0}, "Result should be 0 for an all-zero segmentation."


def test_calculate_lesion_size(mock_segmentation):
    """Test lesion size calculation for a basic segmentation."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation, spacing=(1, 1, 1))
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size matches the number of non-zero pixels
    assert result == {"lesion_size": 5}, "Result should match the number of non-zero pixels for unit spacing."


def test_calculate_lesion_size_with_isotropic_spacing():
    """Test lesion size calculation for a large segmentation."""
    large_segmentation = np.ones((10, 10, 10), dtype=int)
    tumor_features = TumorFeatures(segmentation=large_segmentation, spacing=(2, 2, 2))
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size matches the total number of pixels in the segmentation
    assert result == {"lesion_size": 1000 * 2**3}, "Result should match the total number of pixels for a full segmentation."


def test_calculate_lesion_size_with_non_isotropic_spacing():
    """Test lesion size calculation for a large segmentation with non-unit spacing."""
    large_segmentation = np.ones((10, 10, 10), dtype=int)
    tumor_features = TumorFeatures(segmentation=large_segmentation, spacing=(0.5, 4, 0.5))
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size is scaled correctly by the voxel spacing
    assert result == {"lesion_size": 1000 * 0.5**2 * 4}, "Result should be scaled by the product of the voxel spacing."


def test_calculate_lesion_size_partial_lesion(mock_segmentation):
    """Test lesion size calculation for a segmentation with partial lesions."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation, spacing=(1, 1, 1))
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size matches the number of non-zero pixels
    assert result == {"lesion_size": 5}, "Result should count only non-zero pixels."


def test_calculate_lesion_size_mixed_values(mock_segmentation_multiple_labels):
    """Test lesion size calculation for a segmentation with multiple label values."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation_multiple_labels, spacing=(1, 1, 1))
    result = tumor_features.calculate_lesion_size()

    # Check that the lesion size matches the total number of non-zero pixels
    assert result == {"lesion_size": 6}, "Result should count all non-zero pixels, regardless of label values."


def test_get_tumor_center_mass(mock_segmentation):
    """Test calculation of the tumor center of mass."""
    tumor_features = TumorFeatures(mock_segmentation, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass(label=1)
    expected_center = np.array([1., 1.4, 1.2])

    # Check that the center of mass is calculated
    assert isinstance(result, np.ndarray), "Result should be a numpy array."
    assert len(result) == 3, "Center of mass should have 3 coordinates."
    assert np.isfinite(result).all(), "Center of mass coordinates should be finite."
    assert np.allclose(result, expected_center), f"Expected {expected_center}, got {result}."


def test_get_tumor_center_mass_no_segmentation():
    """Test when segmentation is None."""
    tumor_features = TumorFeatures(segmentation=None, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass()

    # Check that the result is an array of NaN values
    assert np.isnan(result).all(), "Result should be an array of NaN values when segmentation is None."


def test_get_tumor_center_mass_empty_segmentation(mock_zero_segmentation):
    """Test when segmentation is an empty array."""
    tumor_features = TumorFeatures(segmentation=mock_zero_segmentation, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass()

    # Check that the result is an array of NaN values
    assert np.isnan(result).all(), "Result should be an array of NaN values for an empty segmentation."


def test_get_tumor_center_mass_with_spacing(mock_segmentation):
    """Test center of mass calculation with non-unit spacing."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation, spacing=(2, 2, 2))
    result = tumor_features.get_tumor_center_mass(label=1)

    # Check that the center of mass is scaled correctly by voxel spacing
    expected_center = np.array([1., 1.4, 1.2]) * np.array([2, 2, 2])
    assert np.allclose(result, expected_center), f"Expected {expected_center}, got {result}."


def test_get_tumor_center_mass_label_not_present(mock_segmentation_multiple_labels):
    """Test center of mass calculation when the label is not present in the segmentation."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation_multiple_labels, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass(label=3)

    # Check that the result is an array of NaN values when the label is not present
    assert np.isnan(result).all(), "Result should be an array of NaN values for a label not present in the segmentation."


def test_get_tumor_center_mass_label_present(mock_segmentation_multiple_labels):
    """Test center of mass calculation for a specific label."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation_multiple_labels, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass(label=2)

    # Check that the center of mass is calculated correctly for the specified label
    expected_center = np.array([1., 0.5, 1.])
    assert np.allclose(result, expected_center), f"Expected {expected_center}, got {result}."


def test_get_tumor_center_mass_label_with_spacing(mock_segmentation_multiple_labels):
    """Test center of mass calculation for a specific label with non-unit spacing."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation_multiple_labels, spacing=(1, 2, 4))
    result = tumor_features.get_tumor_center_mass(label=2)

    # Check that the center of mass is scaled correctly for the specified label with spacing
    expected_center = np.array([1., 0.5, 1.]) * np.array([1, 2, 4])
    assert np.allclose(result, expected_center), f"Expected {expected_center}, got {result}."


def test_get_tumor_center_mass_large_segmentation():
    """Test center of mass calculation for a large segmentation."""
    large_segmentation = np.ones((10, 10, 10), dtype=int)
    tumor_features = TumorFeatures(segmentation=large_segmentation, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass(label=1)

    # Check that the center of mass is at the center of the cube
    expected_center = np.array([4.5, 4.5, 4.5])
    assert np.allclose(result, expected_center), f"Expected {expected_center}, got {result}."


def test_get_tumor_center_mass_partial_segmentation(mock_segmentation_multiple_labels):
    """Test center of mass calculation for a segmentation with a non-contiguous region."""
    segmentation = mock_segmentation_multiple_labels.copy()
    segmentation[0, 0, 0] = 4
    tumor_features = TumorFeatures(segmentation=segmentation, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_center_mass(label=4)

    # Check that the center of mass is calculated as the mean of all tumor voxels for label 2
    expected_center = np.array([0, 0, 0])
    assert np.allclose(result, expected_center), f"Expected {expected_center}, got {result}."


def test_get_tumor_center_mass_invalid_label(mock_segmentation):
    """Test calculation of the tumor center of mass with an invalid label."""
    tumor_features = TumorFeatures(mock_segmentation)
    result = tumor_features.get_tumor_center_mass(label=3)  # Invalid label

    # Check that the result is NaN for an invalid label
    assert np.isnan(result).all(), "Center of mass should be NaN for an invalid label."


def test_get_tumor_slices(mock_segmentation_multiple_labels):
    """Test calculation of tumor slices for each plane."""
    tumor_features = TumorFeatures(mock_segmentation_multiple_labels)
    axial, coronal, sagittal = tumor_features.get_tumor_slices()

    # Check that the tumor slices are calculated for each plane
    assert isinstance(axial, list), "Axial tumor slices should be a list."
    assert isinstance(coronal, list), "Coronal tumor slices should be a list."
    assert isinstance(sagittal, list), "Sagittal tumor slices should be a list."
    assert len(axial) > 0, "There should be tumor slices in the axial plane."


def test_calculate_tumor_slices(mock_segmentation_multiple_labels):
    """Test calculation of the number of tumor slices."""
    tumor_features = TumorFeatures(mock_segmentation_multiple_labels)
    result = tumor_features.calculate_tumor_slices()

    # Check that the result is a dictionary
    assert isinstance(result, dict), "Result should be a dictionary."
    assert "axial_tumor_slice" in result, "Axial tumor slices should be in the result."
    assert "coronal_tumor_slice" in result, "Coronal tumor slices should be in the result."
    assert "sagittal_tumor_slice" in result, "Sagittal tumor slices should be in the result."


def test_get_tumor_slices_no_segmentation():
    """Test when segmentation is None."""
    tumor_features = TumorFeatures(segmentation=None, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_slices()

    # Check that the result is np.nan for all planes
    assert np.isnan(result[0]).all(), "Axial tumor slices should be np.nan when segmentation is None."
    assert np.isnan(result[1]).all(), "Coronal tumor slices should be np.nan when segmentation is None."
    assert np.isnan(result[2]).all(), "Sagittal tumor slices should be np.nan when segmentation is None."


def test_get_tumor_slices_empty_segmentation(mock_zero_segmentation):
    """Test when segmentation is an empty array (no tumor)."""
    tumor_features = TumorFeatures(segmentation=mock_zero_segmentation, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_slices()

    # Check that all planes have no tumor slices
    assert result[0] == [], "Expected no axial tumor slices for empty segmentation."
    assert result[1] == [], "Expected no coronal tumor slices for empty segmentation."
    assert result[2] == [], "Expected no sagittal tumor slices for empty segmentation."


def test_get_tumor_slices_basic_segmentation(mock_segmentation):
    """Test tumor slice extraction from a simple segmentation."""
    tumor_features = TumorFeatures(segmentation=mock_segmentation, spacing=(1, 1, 1))
    result = tumor_features.get_tumor_slices()

    # Check that the slices with tumors are correctly identified
    expected_axial_slices = [1]
    expected_coronal_slices = [1, 2]
    expected_sagittal_slices = [0, 1, 2]
    assert result[0] == expected_axial_slices, f"Expected axial tumor slices {expected_axial_slices}, got {result[0]}"
    assert result[1] == expected_coronal_slices, f"Expected coronal tumor slices {expected_coronal_slices}, got {result[1]}"
    assert result[2] == expected_sagittal_slices, f"Expected sagittal tumor slices {expected_sagittal_slices}, got {result[2]}"


def test_calculate_position_tumor_slices(mock_segmentation_multiple_labels):
    """Test calculation of the position of tumor slices."""
    tumor_features = TumorFeatures(mock_segmentation_multiple_labels)
    result = tumor_features.calculate_position_tumor_slices()

    # Check that the result contains both lower and upper positions for each plane
    assert "lower_axial_tumor_slice" in result, "Lower axial tumor slice should be in the result."
    assert "upper_axial_tumor_slice" in result, "Upper axial tumor slice should be in the result."
    assert np.isfinite(result["lower_axial_tumor_slice"]), "Lower axial tumor slice should be finite."


def test_calculate_tumor_pixel(mock_segmentation_multiple_labels):
    """Test calculation of tumor pixels."""
    tumor_features = TumorFeatures(mock_segmentation_multiple_labels)
    result = tumor_features.calculate_tumor_pixel()

    # Check that the result contains tumor pixel counts with proper prefixes
    assert "lesion_size_1" in result, "Tumor pixels for label '1' should be in the result."
    assert "lesion_size_2" in result, "Tumor pixels for label '2' should be in the result."

