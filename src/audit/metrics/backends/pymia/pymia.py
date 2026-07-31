import os
from pathlib import Path

import numpy as np
import pandas as pd
import pymia.evaluation.evaluator as eval_
from colorama import Fore
from loguru import logger
from pymia.evaluation.metric import metric
from pymia.evaluation.writer import CSVStatisticsWriter

from audit.io.readers import resolve_configured_format
from audit.io.readers import resolve_reader_options
from audit.metrics.backends.commons import normalize_empty_region_metric
from audit.metrics.backends.commons import standardize_output
from audit.metrics.backends.metric_names import normalize_metric_config
from audit.metrics.backends.metric_names import normalize_metric_names
from audit.metrics.backends.metric_names import validate_metric_names
from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_print
from audit.utils.commons.strings import fancy_tqdm

# pymia 0.3.2 still references the NumPy 1.x alias when a distance metric
# encounters an empty mask. Keep the compatibility local to this adapter.
if not hasattr(np, "Inf"):
    np.Inf = np.inf


def _pivot_and_standardize(raw: list) -> pd.DataFrame:
    """Pivot long-format pymia results and apply shared output contract."""
    df = pd.DataFrame(raw)
    df = df.pivot_table(index=["ID", "region", "model"], columns="metric", values="value")
    df.reset_index(inplace=True)
    return standardize_output(df)


def perform_evaluation(
    pymia_evaluator,
    path_gt,
    path_pred,
    subject,
    modality_name: str = "MRI",
    ground_truth_format: str = None,
    prediction_format: str = None,
    ground_truth_reader_options: dict = None,
    prediction_reader_options: dict = None,
):
    from audit.metrics.backends.commons import load_subject_data
    from audit.utils.modalities.factory import get_modality

    modality = get_modality(modality_name)

    try:
        gt_arr, pred_arr, spacing = load_subject_data(
            path_gt,
            path_pred,
            subject,
            modality_name=modality_name,
            ground_truth_format=ground_truth_format,
            prediction_format=prediction_format,
            ground_truth_reader_options=ground_truth_reader_options,
            prediction_reader_options=prediction_reader_options,
        )

        # Pymia evaluates SimpleITK images. The reader layer already validated
        # shape and supplied spacing aligned with NumPy axes.
        if gt_arr.dtype not in (np.uint8, np.int32):
            gt_arr = gt_arr.astype(np.int32)
        if pred_arr.dtype not in (np.uint8, np.int32):
            pred_arr = pred_arr.astype(np.int32)

        ground_truth = modality.build_image(gt_arr)
        prediction = modality.build_image(pred_arr)
        ground_truth.SetSpacing(tuple(spacing[::-1]))
        prediction.SetSpacing(tuple(spacing[::-1]))
        pymia_evaluator.evaluate(prediction, ground_truth, subject)
        for label_value, label_name in pymia_evaluator.labels.items():
            label_values = label_value if isinstance(label_value, tuple) else [label_value]
            ground_truth_present = bool(np.isin(gt_arr, label_values).any())
            prediction_present = bool(np.isin(pred_arr, label_values).any())
            for result in pymia_evaluator.results:
                if result.id_ == subject and result.label == label_name:
                    result.value = normalize_empty_region_metric(
                        result.metric,
                        result.value,
                        ground_truth_present,
                        prediction_present,
                    )
    except Exception as exc:
        raise RuntimeError(f"Pymia evaluation failed for subject '{subject}': {exc}") from exc

    return pymia_evaluator


def aggregate_results(pymia_evaluator, model_name: str) -> list:
    aggregated = []
    for result in pymia_evaluator.results:
        value = result.value
        if np.isscalar(value) and not np.isfinite(value):
            value = np.nan
        aggregated.append(
            {
                "ID": result.id_,
                "region": result.label,
                "metric": result.metric,
                "value": value,
                "model": model_name,
            }
        )
    return aggregated


def compute_statistics(pymia_evaluator, config, model_name: str):
    functions = {
        "MEAN": np.mean,
        "MEDIAN": np.median,
        "STD": np.std,
        "MIN": np.min,
        "MAX": np.max,
        "Q1": lambda x: np.percentile(x, 25),
        "Q3": lambda x: np.percentile(x, 75),
        "CI_2.5": lambda x: np.percentile(x, 2.5),
        "CI_5": lambda x: np.percentile(x, 5),
        "CI_95": lambda x: np.percentile(x, 95),
        "CI_97.5": lambda x: np.percentile(x, 97.5),
    }
    CSVStatisticsWriter(
        f"{config['output_path']}/stats/{model_name}/{config['filename']}.csv",
        delimiter=",",
        functions=functions,
    ).write(pymia_evaluator.results)


def instantiate_pymia_metrics(selected_metrics: list) -> list:
    """Map config metric keys to pymia metric objects."""
    selected_metrics = normalize_metric_names(selected_metrics, "pymia")
    metric_map = {
        # Overlap
        "ari": (metric.AdjustedRandIndex, {}),
        "auc": (metric.AreaUnderCurve, {}),
        "ckc": (metric.CohenKappaCoefficient, {}),
        "dice": (metric.DiceCoefficient, {}),
        "ic": (metric.InterclassCorrelation, {}),
        "jacc": (metric.JaccardCoefficient, {}),
        "mi": (metric.MutualInformation, {}),
        "rand": (metric.RandIndex, {}),
        "so": (metric.SurfaceOverlap, {}),
        "sdo": (metric.SurfaceDiceOverlap, {}),
        "vs": (metric.VolumeSimilarity, {}),
        # Distance
        "haus": (metric.HausdorffDistance, {"percentile": 100}),
        "avd": (metric.AverageDistance, {}),
        "mahal": (metric.MahalanobisDistance, {}),
        "vi": (metric.VariationOfInformation, {}),
        "gce": (metric.GlobalConsistencyError, {}),
        "prob": (metric.ProbabilisticDistance, {}),
        # Classical
        "sens": (metric.Sensitivity, {}),
        "spec": (metric.Specificity, {}),
        "prec": (metric.Precision, {}),
        "fmeas": (metric.FMeasure, {}),
        "accu": (metric.Accuracy, {}),
        "fallout": (metric.Fallout, {}),
        "fnr": (metric.FalseNegativeRate, {}),
        "tp": (metric.TruePositive, {}),
        "fp": (metric.FalsePositive, {}),
        "tn": (metric.TrueNegative, {}),
        "fn": (metric.FalseNegative, {}),
        "ref_vol": (metric.ReferenceVolume, {}),
        "pred_vol": (metric.PredictionVolume, {}),
    }

    metrics = []
    for metric_name in selected_metrics:
        if metric_name in metric_map:
            metric_class, params = metric_map[metric_name]
            metrics.append(metric_class(metric=metric_name, **params))
        else:
            print(
                f"The '{metric_name}' metric is not available. "
                f"Add it to audit.metrics.backends.pymia.pymia.instantiate_pymia_metrics."
            )
    return metrics


def extract_pymia_metrics(config_file) -> pd.DataFrame:
    labels, processed_labels = config_file["labels"], {}
    for key, value in labels.items():
        if value != 0:
            if isinstance(value, list):
                value = tuple(value)
            processed_labels[value] = key

    path_ground_truth_dataset = config_file["data_path"]
    metrics_config = normalize_metric_config(config_file["metrics"], "pymia")
    metrics_to_extract = [key for key, value in metrics_config.items() if value]
    validate_metric_names(metrics_to_extract, "pymia")
    subjects_list = list_dirs(path_ground_truth_dataset)
    modality_name = config_file.get("modality", "MRI")
    ground_truth_format = resolve_configured_format(config_file, "segmentation", modality_name)
    prediction_format = resolve_configured_format(config_file, "prediction", modality_name)
    ground_truth_reader_options = resolve_reader_options(config_file, "segmentation")
    prediction_reader_options = resolve_reader_options(config_file, "prediction")

    pymia_metrics = instantiate_pymia_metrics(metrics_to_extract)
    evaluator = eval_.SegmentationEvaluator(pymia_metrics, processed_labels)

    models = config_file["model_predictions_paths"]
    # Accumulate results across ALL models before pivoting
    all_raw_metrics = []

    for model_name, path_predictions in models.items():
        fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
        logger.info(f"Starting metric extraction for model {model_name}")

        with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
            for n, subject_id in enumerate(subjects_list):
                pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
                pbar.update(1)
                if n % 10 == 0 and n > 0:
                    fancy_print(f"Processed {n} subjects", Fore.CYAN, "🔹")

                logger.info(f"Processing subject: {subject_id}")
                evaluator = perform_evaluation(
                    evaluator,
                    path_ground_truth_dataset,
                    path_predictions,
                    subject_id,
                    modality_name=modality_name,
                    ground_truth_format=ground_truth_format,
                    prediction_format=prediction_format,
                    ground_truth_reader_options=ground_truth_reader_options,
                    prediction_reader_options=prediction_reader_options,
                )

        # collect this model's results, then clear the evaluator for the next model
        all_raw_metrics.extend(aggregate_results(evaluator, model_name))

        if config_file.get("calculate_stats", None):
            Path(os.path.join(config_file["output_path"], "stats", f"{model_name}")).mkdir(parents=True, exist_ok=True)
            compute_statistics(evaluator, config_file, model_name)

        evaluator.clear()
        logger.info(f"Finishing metric extraction for model {model_name}")

    return _pivot_and_standardize(all_raw_metrics)
