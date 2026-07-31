"""
Shared utilities for all metric backends.

Any helper that is common across backends (multiprocessing setup, subject data
loading, …) lives here so that each backend module stays focused on its own
computation logic.
"""

import os

import numpy as np
from loguru import logger

from audit.io.readers import read_subject_image


@logger.catch
def check_multiprocessing(config_file) -> int:
    """Return a validated CPU-core count from the config file."""
    cpu_cores = config_file.get("cpu_cores")
    if cpu_cores is None or cpu_cores == "None":
        logger.info("cpu_cores not specified or invalid in config, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()
    if not isinstance(cpu_cores, int) or cpu_cores <= 0:
        logger.info(f"Invalid cpu_cores value: {cpu_cores}, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()
    logger.info(f"Using {cpu_cores} CPU cores for processing")
    return cpu_cores


def initializer(shared_df, lock):
    """Initialise shared variables for multiprocessing workers."""
    global shared_dataframe, dataframe_lock
    shared_dataframe = shared_df
    dataframe_lock = lock


def normalize_empty_region_metric(
    metric_name: str,
    value: float,
    ground_truth_present: bool,
    prediction_present: bool,
) -> float:
    """Normalize equivalent backend metrics for empty label masks."""
    if ground_truth_present and prediction_present:
        return value

    equivalents = {
        "dsc": "dice",
        "jacc": "jaccard",
        "iou": "jaccard",
        "accu": "accuracy",
        "prec": "precision",
        "ppv": "precision",
        "sens": "sensitivity",
        "spec": "specificity",
        "haus": "hausdorff_distance",
        "hd": "hausdorff_distance",
        "pred_vol": "predicted_size",
        "numb_pred": "predicted_size",
    }
    metric_name = equivalents.get(metric_name, metric_name)

    if not ground_truth_present and not prediction_present:
        return {
            "dice": 1.0,
            "jaccard": 1.0,
            "accuracy": 1.0,
            "precision": 0.0,
            "sensitivity": np.nan,
            "specificity": 1.0,
            "hausdorff_distance": 0.0,
            "predicted_size": 0.0,
        }.get(metric_name, value)

    if ground_truth_present:
        return {
            "dice": 0.0,
            "jaccard": 0.0,
            "precision": 0.0,
            "sensitivity": 0.0,
            "hausdorff_distance": np.nan,
            "predicted_size": 0.0,
        }.get(metric_name, value)

    return {
        "dice": 0.0,
        "jaccard": 0.0,
        "precision": 0.0,
        "sensitivity": np.nan,
        "hausdorff_distance": np.nan,
    }.get(metric_name, value)


def load_subject_data(
    path_ground_truth_dataset: str,
    path_predictions: str,
    subject_id: str,
    modality_name: str = "MRI",
    ground_truth_format: str = None,
    prediction_format: str = None,
    ground_truth_reader_options: dict = None,
    prediction_reader_options: dict = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load ground-truth and prediction arrays for a single subject.

    Uses the shared format-reader layer so every backend loads MRI and US data
    with the same naming, shape, and physical-spacing rules.

    Returns
    -------
    gt : np.ndarray
        Ground-truth segmentation array.
    pred : np.ndarray
        Predicted segmentation array.
    spacing : np.ndarray
        Ground-truth spacing in NumPy axis order.
    """
    from audit.utils.modalities.factory import get_modality

    modality = get_modality(modality_name)
    ground_truth_format = ground_truth_format or modality.get_default_format()
    prediction_format = prediction_format or ground_truth_format
    gt_data = read_subject_image(
        path_ground_truth_dataset,
        subject_id,
        "_seg",
        ground_truth_format,
        **(ground_truth_reader_options or {}),
    )
    pred_data = read_subject_image(
        path_predictions,
        subject_id,
        "_pred",
        prediction_format,
        **(prediction_reader_options or {}),
    )

    if gt_data.array.shape != pred_data.array.shape:
        raise ValueError(
            f"Shape mismatch for {subject_id}: ground truth {gt_data.array.shape}, "
            f"prediction {pred_data.array.shape}."
        )
    if gt_data.spacing.shape != pred_data.spacing.shape or not np.allclose(gt_data.spacing, pred_data.spacing):
        raise ValueError(
            f"Spacing mismatch for {subject_id}: ground truth {gt_data.spacing.tolist()}, "
            f"prediction {pred_data.spacing.tolist()}."
        )

    return gt_data.array, pred_data.array, gt_data.spacing


def standardize_output(df: "pd.DataFrame") -> "pd.DataFrame":
    """Return a consistently formatted metrics DataFrame.

    * Columns: ``ID``, ``region``, ``model`` first, then metric columns
      sorted alphabetically.
    * Rows sorted by ``model`` → ``ID`` → ``region`` (all ascending).
    * Pivot table column-level name removed if present.
    """
    import pandas as pd  # local import — commons must stay lightweight

    # Drop the pivot column-level name introduced by pivot_table (e.g. "metric")
    df.columns.name = None

    key_cols = ["ID", "region", "model"]
    metric_cols = sorted(c for c in df.columns if c not in key_cols)
    df = df[key_cols + metric_cols]
    df = df.sort_values(by=["model", "ID", "region"], ascending=True).reset_index(drop=True)
    return df
