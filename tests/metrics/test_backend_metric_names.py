import numpy as np
import pytest

from audit.metrics.backends.metric_names import AUDIT_METRICS
from audit.metrics.backends.metric_names import METRICS_RELOADED_METRICS
from audit.metrics.backends.metric_names import PYMIA_METRICS
from audit.metrics.backends.metric_names import backend_metric_pairs
from audit.metrics.backends.metric_names import normalize_metric_config
from audit.metrics.backends.metric_names import validate_metric_names
from audit.metrics.backends.metrics_reloaded.metrics.pairwise_measures import BinaryPairwiseMeasures
from audit.metrics.backends.pymia.pymia import instantiate_pymia_metrics


def test_each_backend_exposes_its_complete_metric_catalog():
    assert len(AUDIT_METRICS) == 8
    assert len(PYMIA_METRICS) == 30
    assert len(METRICS_RELOADED_METRICS) == 30
    assert {"ari", "mahal", "pred_vol", "accu", "haus"} <= set(PYMIA_METRICS)
    assert {"cd", "mae", "mse", "rmse", "nrmse"}.isdisjoint(PYMIA_METRICS)
    assert {"dsc", "cldice", "hd_perc", "wck"} <= set(METRICS_RELOADED_METRICS)


def test_backend_catalogs_match_their_executable_wrappers():
    assert len(instantiate_pymia_metrics(list(PYMIA_METRICS))) == len(PYMIA_METRICS)
    binary = BinaryPairwiseMeasures(np.array([0, 1]), np.array([0, 1]))
    assert set(binary.measures_dict) == set(METRICS_RELOADED_METRICS)


def test_metricsreloaded_avdr_does_not_underflow_unsigned_masks():
    reference = np.array([1, 0, 0], dtype=np.uint8)
    prediction = np.array([1, 1, 1], dtype=np.uint8)

    binary = BinaryPairwiseMeasures(prediction, reference)

    assert binary.absolute_volume_difference_ratio() == pytest.approx(2.0)


def test_metricsreloaded_binary_weighted_kappa_is_executable():
    reference = np.array([0, 0, 1, 1], dtype=np.uint8)
    prediction = np.array([0, 1, 1, 1], dtype=np.uint8)
    binary = BinaryPairwiseMeasures(prediction, reference)

    assert binary.weighted_cohens_kappa() == pytest.approx(binary.cohens_kappa())


def test_third_party_backend_names_are_preserved():
    assert backend_metric_pairs(["dsc", "iou", "ppv", "hd", "numb_pred"], "metricsreloaded") == [
        ("dsc", "dsc"),
        ("iou", "iou"),
        ("ppv", "ppv"),
        ("hd", "hd"),
        ("numb_pred", "numb_pred"),
    ]


def test_metric_from_another_backend_is_rejected():
    with pytest.raises(ValueError, match="backend 'metricsreloaded'"):
        validate_metric_names(["dice"], "metricsreloaded")
    with pytest.raises(ValueError, match="backend 'pymia'"):
        validate_metric_names(["dsc"], "pymia")


def test_legacy_audit_names_are_normalized_for_compatibility():
    assert normalize_metric_config(
        {
            "dice": True,
            "jacc": True,
            "accu": True,
            "prec": True,
            "sens": True,
            "spec": True,
            "haus": True,
            "size": True,
        },
        "audit",
    ) == {
        "dice": True,
        "jaccard": True,
        "accuracy": True,
        "precision": True,
        "sensitivity": True,
        "specificity": True,
        "hausdorff_distance": True,
        "predicted_size": True,
    }


def test_audit_aliases_are_not_applied_to_third_party_backends():
    assert normalize_metric_config({"haus": True}, "pymia") == {"haus": True}
    with pytest.raises(ValueError, match="backend 'pymia'"):
        normalize_metric_config({"hausdorff_distance": True}, "pymia")


def test_duplicate_audit_legacy_and_canonical_names_are_rejected():
    with pytest.raises(ValueError, match="configured more than once"):
        normalize_metric_config({"accuracy": True, "accu": True}, "audit")
