import pandas as pd

from audit.utils.internal._csv_helpers import normalize_metric_columns


def test_legacy_audit_metric_columns_are_normalized_without_renaming_backend_specific_metrics():
    legacy = pd.DataFrame(
        {
            "DICE": [0.9],
            "HAUS": [2.0],
            "hd": [2.5],
            "JACC": [0.81],
            "iou": [0.8],
            "ACCU": [0.95],
            "PREC": [0.85],
            "SPEC": [0.98],
            "SENS": [0.87],
            "SIZE": [100.0],
            "pred_vol": [100.0],
        }
    )

    normalized = normalize_metric_columns(legacy)

    assert {
        "dice",
        "hausdorff_distance",
        "jaccard",
        "accuracy",
        "precision",
        "specificity",
        "sensitivity",
        "predicted_size",
    } <= set(normalized.columns)
    assert {"hd", "iou", "pred_vol"} <= set(normalized.columns)
