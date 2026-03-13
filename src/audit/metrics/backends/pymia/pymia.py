import os
from pathlib import Path

import numpy as np
import pandas as pd
import pymia.evaluation.evaluator as eval_
import SimpleITK as sitk
from colorama import Fore
from loguru import logger
from pymia.evaluation.metric import metric
from pymia.evaluation.writer import CSVStatisticsWriter

from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_print
from audit.utils.commons.strings import fancy_tqdm
from audit.metrics.backends.commons import standardize_output


def _pivot_and_standardize(raw: list) -> pd.DataFrame:
    """Pivot long-format pymia results and apply shared output contract."""
    df = pd.DataFrame(raw)
    df = df.pivot_table(index=["ID", "region", "model"], columns="metric", values="value")
    df.reset_index(inplace=True)
    return standardize_output(df)


def perform_evaluation(pymia_evaluator, path_gt, path_pred, subject):
    path_gt = os.path.join(str(path_gt), subject, f"{subject}_seg.nii.gz")
    path_pred = os.path.join(str(path_pred), subject, f"{subject}_pred.nii.gz")

    try:
        if not os.path.exists(path_gt):
            raise FileNotFoundError(f'Ground truth file "{path_gt}" does not exist')
        if not os.path.exists(path_pred):
            raise FileNotFoundError(f'Prediction file "{path_pred}" does not exist')

        ground_truth = sitk.ReadImage(path_gt)
        prediction = sitk.ReadImage(path_pred)
        pymia_evaluator.evaluate(prediction, ground_truth, subject)
    except Exception as e:
        print(f"{subject} -> {e}")

    return pymia_evaluator


def aggregate_results(pymia_evaluator, model_name: str) -> list:
    return [
        {
            "ID": result.id_,
            "region": result.label,
            "metric": result.metric,
            "value": result.value,
            "model": model_name,
        }
        for result in pymia_evaluator.results
    ]


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
    metric_map = {
        # Regression
        "cd": (metric.CoefficientOfDetermination, {}),
        "mae": (metric.MeanAbsoluteError, {}),
        "mse": (metric.MeanSquaredError, {}),
        "rmse": (metric.RootMeanSquaredError, {}),
        "nrmse": (metric.NormalizedRootMeanSquaredError, {}),
        
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
        if isinstance(value, list):
            value = tuple(value)
        processed_labels[value] = key

    path_ground_truth_dataset = config_file["data_path"]
    metrics_to_extract = [key for key, value in config_file["metrics"].items() if value]
    subjects_list = list_dirs(path_ground_truth_dataset)

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
                evaluator = perform_evaluation(evaluator, path_ground_truth_dataset, path_predictions, subject_id)

        # collect this model's results, then clear the evaluator for the next model
        all_raw_metrics.extend(aggregate_results(evaluator, model_name))

        if config_file.get("calculate_stats", None):
            Path(os.path.join(config_file["output_path"], "stats", f"{model_name}")).mkdir(
                parents=True, exist_ok=True
            )
            compute_statistics(evaluator, config_file, model_name)

        evaluator.clear()
        logger.info(f"Finishing metric extraction for model {model_name}")

    return _pivot_and_standardize(all_raw_metrics)
