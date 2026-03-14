import os
import warnings
from multiprocessing import Lock
from multiprocessing import Manager
from multiprocessing import Pool

import pandas as pd
from colorama import Fore
from loguru import logger

from audit.metrics.backends.commons import check_multiprocessing
from audit.metrics.backends.commons import initializer
from audit.metrics.backends.commons import load_subject_data
from audit.metrics.backends.commons import standardize_output
from audit.metrics.backends.metrics_reloaded.processes.mixed_measures_processes import MultiLabelPairwiseMeasures
from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_print
from audit.utils.commons.strings import fancy_tqdm

warnings.filterwarnings("ignore")


def process_subject_metricsreloaded(shared_df, params: dict, cpu_cores: int):
    """Compute MetricsReloaded metrics for a single subject."""
    # Use the shared loader — same convention as all other backends
    gt, pred, spacing = load_subject_data(
        params["path_ground_truth_dataset"],
        params["path_predictions"],
        params["subject_id"],
    )

    list_values = [v for v in params["numeric_label"] if v != 0]
    mlpm = MultiLabelPairwiseMeasures(
        [pred],
        [gt],
        [None],
        list_values=list_values,
        measures_pcc=params["metrics_to_extract"],
        per_case=True,
        pixdim=spacing,
    )
    df_seg, _ = mlpm.per_label_dict()

    label_to_region = dict(zip(params["numeric_label"], params["label_names"]))
    results = []
    for _, row in df_seg.iterrows():
        region = label_to_region[row["label"]]
        for metric_name in params["metrics_to_extract"]:
            if metric_name in row:
                value = row[metric_name]
                results.append(
                    {
                        "ID": params["subject_id"],
                        "region": region,
                        "metric": metric_name,
                        "value": float(value) if value is not None else float("nan"),
                        "model": params["model_name"],
                    }
                )

    df_metrics = pd.DataFrame(results)

    if cpu_cores == 1:
        return df_metrics

    # multiprocessing path
    with dataframe_lock:
        shared_df[params["subject_id"]] = df_metrics

    return None


def extract_metricsreloaded_metrics(config_file) -> pd.DataFrame:
    label_names = list(config_file["labels"].keys())
    numeric_label = list(config_file["labels"].values())
    path_ground_truth_dataset = config_file["data_path"]
    metrics_to_extract = [key for key, value in config_file["metrics"].items() if value]
    subjects_list = list_dirs(path_ground_truth_dataset)
    models = config_file["model_predictions_paths"]
    cpu_cores = check_multiprocessing(config_file)

    raw_metrics = pd.DataFrame()

    if cpu_cores == 1:
        for model_name, path_predictions in models.items():
            fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
            logger.info(f"Starting metric extraction for model {model_name}")

            with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                for subject_id in subjects_list:
                    pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
                    pbar.update(1)

                    params = {
                        "path_ground_truth_dataset": path_ground_truth_dataset,
                        "path_predictions": path_predictions,
                        "numeric_label": numeric_label,
                        "subject_id": subject_id,
                        "label_names": label_names,
                        "metrics_to_extract": metrics_to_extract,
                        "model_name": model_name,
                    }

                    df_subject = process_subject_metricsreloaded(None, params, cpu_cores)
                    raw_metrics = pd.concat([raw_metrics, df_subject], ignore_index=True)

            logger.info(f"Finishing metric extraction for model {model_name}")

    else:
        manager = Manager()
        shared_data = manager.dict()
        lock = Lock()

        with Pool(processes=cpu_cores, initializer=initializer, initargs=(shared_data, lock)) as pool:
            for model_name, path_predictions in models.items():
                fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
                logger.info(f"Starting metric extraction for model {model_name}")

                tasks = []
                for subject_id in subjects_list:
                    params = {
                        "path_ground_truth_dataset": path_ground_truth_dataset,
                        "path_predictions": path_predictions,
                        "numeric_label": numeric_label,
                        "subject_id": subject_id,
                        "label_names": label_names,
                        "metrics_to_extract": metrics_to_extract,
                        "model_name": model_name,
                    }
                    tasks.append(
                        pool.apply_async(process_subject_metricsreloaded, args=(shared_data, params, cpu_cores))
                    )

                with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                    for task in tasks:
                        task.wait()
                        pbar.update(1)

                for subject_id, df_subject in shared_data.items():
                    raw_metrics = pd.concat([raw_metrics, df_subject], ignore_index=True)
                shared_data.clear()

                logger.info(f"Finishing metric extraction for model {model_name}")

    raw_metrics = raw_metrics.pivot_table(
        index=["ID", "region", "model"],
        columns="metric",
        values="value",
    ).reset_index()
    return standardize_output(raw_metrics)
