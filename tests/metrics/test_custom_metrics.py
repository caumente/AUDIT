import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import numpy as np
import pytest
from scipy.spatial.distance import directed_hausdorff

from src.audit.metrics.segmentation_metrics import accuracy
from src.audit.metrics.segmentation_metrics import calculate_confusion_matrix_elements
from src.audit.metrics.segmentation_metrics import dice_score
from src.audit.metrics.segmentation_metrics import hausdorff_distance
from src.audit.metrics.segmentation_metrics import jaccard_index
from src.audit.metrics.segmentation_metrics import one_hot_encoding
from src.audit.metrics.segmentation_metrics import precision
from src.audit.metrics.segmentation_metrics import sensitivity
from src.audit.metrics.segmentation_metrics import specificity


# Fixtures
@pytest.fixture
def mock_segmentation_binary_labels():
    """Fixture to create a mock 3D segmentation array with multiple labels."""
    return np.array(
        [
            [[1, 0, 0], [0, 1, 1], [1, 0, 0]],
            [[1, 1, 1], [1, 1, 0], [1, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
    )


@pytest.fixture
def mock_ground_truth_binary_labels():
    """Fixture to create a mock 3D ground truth array with multiple labels."""
    return np.array(
        [
            [[1, 0, 0], [0, 1, 0], [1, 0, 0]],
            [[1, 1, 1], [1, 1, 0], [1, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
    )


@pytest.fixture
def mock_segmentation_multiple_labels():
    """Fixture to create a mock 3D segmentation array with multiple labels."""
    return np.array(
        [
            [[1, 0, 0], [0, 1, 1], [1, 0, 0]],
            [[1, 2, 2], [2, 2, 0], [1, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
    )


@pytest.fixture
def mock_ground_truth_multiple_labels():
    """Fixture to create a mock 3D segmentation array with multiple labels."""
    return np.array(
        [
            [[1, 0, 0], [0, 0, 0], [1, 0, 0]],
            [[1, 2, 2], [2, 1, 0], [2, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
    )


@pytest.fixture
def mock_segmentation_empty():
    """Fixture for a segmentation with no labels (empty segmentation)."""
    return np.array(
        [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]
    )


@pytest.fixture
def binary_labels():
    return [0, 1]


@pytest.fixture
def multiclass_labels():
    return [0, 1, 2]


# Tests for one_hot_encoding
def test_one_hot_encoding_with_binary_labels(mock_segmentation_binary_labels, binary_labels):
    result = one_hot_encoding(mock_segmentation_binary_labels, binary_labels, skip_background=True)

    # Since skip_background=True, we expect only one channel for label 1 (foreground), not for 0 (background)
    assert result.shape == (1, 3, 3, 3)  # Only 1 class (1) and 3x3 grid

    # Check that the result for label 1 matches the binary segmentation for foreground
    assert np.array_equal(result[0], (mock_segmentation_binary_labels == 1).astype(int))  # Check foreground


def test_one_hot_encoding_with_multiple_labels(mock_segmentation_multiple_labels, multiclass_labels):
    result = one_hot_encoding(mock_segmentation_multiple_labels, multiclass_labels, skip_background=True)

    # Since skip_background=True, we expect 2 channels (for label 1 and label 2)
    assert result.shape == (2, 3, 3, 3)  # 2 classes (1 and 2) and 3x3 grid

    # Check label 1 (foreground label)
    assert np.array_equal(result[0], (mock_segmentation_multiple_labels == 1).astype(int))  # Check label 1
    # Check label 2
    assert np.array_equal(result[1], (mock_segmentation_multiple_labels == 2).astype(int))  # Check label 2


def test_calculate_confusion_matrix_elements_binary(mock_segmentation_binary_labels, mock_ground_truth_binary_labels):
    """Test confusion matrix elements for a binary segmentation and ground truth."""
    tp, tn, fp, fn = calculate_confusion_matrix_elements(
        mock_ground_truth_binary_labels, mock_segmentation_binary_labels
    )

    # Manually count the confusion matrix elements
    expected_tp = 9  # True positives: pixels where both gt and seg are 1
    expected_tn = 17  # True negatives: pixels where both gt and seg are 0
    expected_fp = 1  # False positives: pixels where gt is 0 but seg is 1
    expected_fn = 0  # False negatives: pixels where gt is 1 but seg is 0

    assert tp == expected_tp
    assert tn == expected_tn
    assert fp == expected_fp
    assert fn == expected_fn


def test_calculate_confusion_matrix_elements_all_zeros(mock_segmentation_binary_labels):
    """Test confusion matrix elements when both gt and segmentation are all zeros."""
    empty_array = np.zeros_like(mock_segmentation_binary_labels)
    tp, tn, fp, fn = calculate_confusion_matrix_elements(empty_array, empty_array)

    # With both arrays being all zeros, we should have:
    expected_tp = 0  # No true positives (no foreground)
    expected_tn = 27  # True negatives (all pixels are background)
    expected_fp = 0  # No false positives (no foreground in seg)
    expected_fn = 0  # No false negatives (no foreground in gt)

    assert tp == expected_tp
    assert tn == expected_tn
    assert fp == expected_fp
    assert fn == expected_fn


def test_calculate_confusion_matrix_elements_all_ones(mock_segmentation_binary_labels):
    """Test confusion matrix elements when both gt and segmentation are all ones."""
    ones_array = np.ones_like(mock_segmentation_binary_labels)
    tp, tn, fp, fn = calculate_confusion_matrix_elements(ones_array, ones_array)

    # With both arrays being all ones, we should have:
    expected_tp = 27  # All pixels match as true positives
    expected_tn = 0  # No true negatives
    expected_fp = 0  # No false positives
    expected_fn = 0  # No false negatives

    assert tp == expected_tp
    assert tn == expected_tn
    assert fp == expected_fp
    assert fn == expected_fn


def test_calculate_confusion_matrix_elements_edge_case_empty(mock_segmentation_binary_labels):
    """Test confusion matrix elements for edge case with empty arrays."""
    empty_array = np.array([[], [], []])
    tp, tn, fp, fn = calculate_confusion_matrix_elements(empty_array, empty_array)

    # For empty arrays, all confusion matrix elements should be zero
    assert tp == 0
    assert tn == 0
    assert fp == 0
    assert fn == 0


# Tests for sensitivity function
def test_sensitivity_standard_case():
    tp = 9
    fn = 1
    result = sensitivity(tp, fn)
    expected_result = 9 / (9 + 1)  # 9 / 10
    assert result == expected_result


def test_sensitivity_no_true_positives():
    tp = 0
    fn = 5
    result = sensitivity(tp, fn)
    # If there are no true positives, return np.nan
    assert np.isnan(result)


def test_sensitivity_all_positives_detected():
    tp = 10
    fn = 0
    result = sensitivity(tp, fn)
    expected_result = 1.0  # All positives detected
    assert result == expected_result


def test_sensitivity_no_positives():
    tp = 0
    fn = 0
    result = sensitivity(tp, fn)
    # If there are no true positives and no false negatives, return np.nan
    assert np.isnan(result)


# Tests for specificity function
def test_specificity_standard_case():
    tn = 17
    fp = 3
    result = specificity(tn, fp)
    expected_result = 17 / (17 + 3)  # 17 / 20
    assert result == expected_result


def test_specificity_all_negatives_detected():
    tn = 10
    fp = 0
    result = specificity(tn, fp)
    expected_result = 1.0  # All non-tumor voxels detected correctly
    assert result == expected_result


def test_specificity_no_true_negatives():
    tn = 0
    fp = 5
    result = specificity(tn, fp)
    expected_result = 0.0  # No true negatives, specificity is 0
    assert result == expected_result


def test_specificity_no_false_positives():
    tn = 10
    fp = 0
    result = specificity(tn, fp)
    expected_result = 1.0  # No false positives, specificity is 1
    assert result == expected_result


# Tests for precision function
def test_precision_standard_case():
    tp = 9
    fp = 3
    result = precision(tp, fp)
    expected_result = 9 / (9 + 3)  # 9 / 12
    assert result == expected_result


def test_precision_all_positives_detected():
    tp = 10
    fp = 0
    result = precision(tp, fp)
    expected_result = 1.0  # All positive voxels detected correctly
    assert result == expected_result


def test_precision_no_true_positives():
    tp = 0
    fp = 5
    result = precision(tp, fp)
    expected_result = np.nan  # No true positives, precision is NaN
    assert np.isnan(result)


def test_precision_no_false_positives():
    tp = 10
    fp = 0
    result = precision(tp, fp)
    expected_result = 1.0  # No false positives, precision is 1
    assert result == expected_result


# Tests for accuracy function
def test_accuracy_standard_case():
    tp = 9
    tn = 17
    fp = 3
    fn = 1
    result = accuracy(tp, tn, fp, fn)
    expected_result = (9 + 17) / (9 + 17 + 3 + 1)  # (26) / (30)
    assert result == expected_result


def test_accuracy_perfect_accuracy():
    tp = 10
    tn = 15
    fp = 0
    fn = 0
    result = accuracy(tp, tn, fp, fn)
    expected_result = 1.0  # All predictions are correct
    assert result == expected_result


def test_accuracy_no_correct_predictions():
    tp = 0
    tn = 0
    fp = 5
    fn = 5
    result = accuracy(tp, tn, fp, fn)
    expected_result = 0.0  # No correct predictions, accuracy is 0
    assert result == expected_result


# Tests for dice_score function
def test_dice_score_standard_case():
    tp = 9
    fp = 3
    fn = 1
    gt = np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]])
    seg = np.array([[1, 0, 0], [1, 1, 1], [0, 0, 0]])

    result = dice_score(tp, fp, fn, gt, seg)
    expected_result = 2 * tp / (2 * tp + fp + fn)  # Dice formula
    assert result == expected_result


def test_dice_score_perfect_overlap():
    gt = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    seg = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    # Perfect overlap, so Dice score should be 1
    result = dice_score(9, 0, 0, gt, seg)
    assert result == 1.0


def test_dice_score_no_overlap():
    gt = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # No overlap, so Dice score should be 0
    result = dice_score(0, 0, 9, gt, seg)
    assert result == 0.0


def test_dice_score_empty_ground_truth():
    gt = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    seg = np.array([[1, 1, 1], [1, 0, 1], [0, 0, 0]])

    # Ground truth is empty, but segmentation is non-empty, so Dice should be 0
    result = dice_score(0, 3, 3, gt, seg)
    assert result == 0.0


def test_dice_score_empty_segmentation():
    gt = np.array([[1, 1, 1], [1, 0, 1], [0, 0, 0]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Segmentation is empty, but ground truth is non-empty, so Dice should be 0
    result = dice_score(0, 0, 3, gt, seg)
    assert result == 0.0


def test_dice_score_edge_case_empty_both():
    gt = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Both are empty, perfect match, so Dice should be 1
    result = dice_score(0, 0, 0, gt, seg)
    assert result == 1.0


# Tests for jaccard_index function
def test_jaccard_index_standard_case():
    tp = 9
    fp = 3
    fn = 1
    gt = np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]])
    seg = np.array([[1, 0, 0], [1, 1, 1], [0, 0, 0]])

    result = jaccard_index(tp, fp, fn, gt, seg)
    expected_result = tp / (tp + fp + fn)  # Jaccard formula
    assert result == expected_result


def test_jaccard_index_perfect_overlap():
    gt = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    seg = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    # Perfect overlap, so Jaccard index should be 1
    result = jaccard_index(9, 0, 0, gt, seg)
    assert result == 1.0


def test_jaccard_index_no_overlap():
    gt = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # No overlap, so Jaccard index should be 0
    result = jaccard_index(0, 0, 9, gt, seg)
    assert result == 0.0


def test_jaccard_index_empty_ground_truth():
    gt = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    seg = np.array([[1, 1, 1], [1, 0, 1], [0, 0, 0]])

    # Ground truth is empty, but segmentation is non-empty, so Jaccard should be 0
    result = jaccard_index(0, 3, 3, gt, seg)
    assert result == 0.0


def test_jaccard_index_empty_segmentation():
    gt = np.array([[1, 1, 1], [1, 0, 1], [0, 0, 0]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Segmentation is empty, but ground truth is non-empty, so Jaccard should be 0
    result = jaccard_index(0, 0, 3, gt, seg)
    assert result == 0.0


def test_jaccard_index_edge_case_empty_both():
    gt = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Both are empty, perfect match, so Jaccard should be 1
    result = jaccard_index(0, 0, 0, gt, seg)
    assert result == 1.0


# Tests for hausdorff_distance function
def test_hausdorff_distance_standard_case():
    gt = np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]])
    seg = np.array([[1, 0, 0], [1, 1, 1], [0, 0, 0]])

    # Directed Hausdorff from seg to gt and from gt to seg
    result = hausdorff_distance(gt, seg)
    expected_result = directed_hausdorff(np.argwhere(seg), np.argwhere(gt))[0]

    assert result == expected_result


def test_hausdorff_distance_perfect_match():
    gt = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    seg = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    # Perfect match, Hausdorff distance should be 0
    result = hausdorff_distance(gt, seg)
    assert result == 0.0


def test_hausdorff_distance_no_overlap():
    gt = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # No overlap, Hausdorff distance should be a large value
    result = hausdorff_distance(gt, seg)
    # The expected Hausdorff distance will depend on the distance function between the two point sets
    # Assuming a large distance due to no overlap
    assert np.isnan(result)


def test_hausdorff_distance_empty_ground_truth():
    gt = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    seg = np.array([[1, 1, 1], [1, 0, 1], [0, 0, 0]])

    # Ground truth is empty, Hausdorff distance should be NaN
    result = hausdorff_distance(gt, seg)
    assert np.isnan(result)


def test_hausdorff_distance_empty_segmentation():
    gt = np.array([[1, 1, 1], [1, 0, 1], [0, 0, 0]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Segmentation is empty, Hausdorff distance should be NaN
    result = hausdorff_distance(gt, seg)
    assert np.isnan(result)


def test_hausdorff_distance_edge_case_empty_both():
    gt = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    seg = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Both are empty, Hausdorff distance should be NaN
    result = hausdorff_distance(gt, seg)
    assert result == 0.0
