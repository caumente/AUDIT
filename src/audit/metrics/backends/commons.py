"""
Shared utilities for all metric backends.

Any helper that is common across backends (multiprocessing setup, subject data
loading, …) lives here so that each backend module stays focused on its own
computation logic.
"""

import os

import numpy as np
from loguru import logger

from audit.utils.sequences.sequences import get_spacing
from audit.utils.sequences.sequences import load_nii_by_subject_id


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


def load_subject_data(
    path_ground_truth_dataset: str,
    path_predictions: str,
    subject_id: str,
) -> tuple[np.ndarray, np.ndarray, tuple]:
    """Load ground-truth and prediction arrays for a single subject.

    Uses the project's ``load_nii_by_subject_id`` utility so that all backends
    follow the same file-naming convention::

        <root>/<subject_id>/<subject_id>_seg.nii.gz   (ground truth)
        <root>/<subject_id>/<subject_id>_pred.nii.gz  (prediction)

    Returns
    -------
    gt : np.ndarray
        Ground-truth segmentation array.
    pred : np.ndarray
        Predicted segmentation array.
    spacing : tuple
        Voxel spacing extracted from the prediction image.
    """
    gt = load_nii_by_subject_id(root_dir=path_ground_truth_dataset, subject_id=subject_id, as_array=True)
    pred_img = load_nii_by_subject_id(root_dir=path_predictions, subject_id=subject_id, seq="_pred")
    pred = load_nii_by_subject_id(root_dir=path_predictions, subject_id=subject_id, seq="_pred", as_array=True)
    spacing = get_spacing(pred_img)
    return gt, pred, spacing


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
