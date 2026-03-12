import os
from multiprocessing import Manager, Lock, Pool
from pathlib import Path

import pandas as pd
from loguru import logger
from colorama import Fore
import nibabel as nib

from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_print, fancy_tqdm
from audit.metrics.main import check_multiprocessing
from src.audit.metrics.backends.MetricsReloaded.processes.mixed_measures_processes import MultiLabelPairwiseMeasures

import warnings

warnings.filterwarnings("ignore")


def initializer(shared_df, lock):
    global shared_dataframe, dataframe_lock
    shared_dataframe = shared_df
    dataframe_lock = lock



def process_subject_metricsreloaded(shared_df, params: dict, cpu_cores: int):
    path_gt = os.path.join(params["path_ground_truth_dataset"], params["subject_id"],
                           f"{params['subject_id']}_seg.nii.gz")
    path_pred = os.path.join(params["path_predictions"], params["subject_id"],
                             f"{params['subject_id']}_pred.nii.gz")

    gt = nib.load(path_gt).get_fdata()
    pred = nib.load(path_pred).get_fdata()

    list_values = [v for v in params["numeric_label"] if v != 0]
    list_pred = [pred]
    list_ref = [gt]
    list_prob = [None]

    mlpm = MultiLabelPairwiseMeasures(
        list_pred,
        list_ref,
        list_prob,
        list_values=list_values,
        measures_pcc=params["metrics_to_extract"],
        per_case=True
    )
    df_seg, _ = mlpm.per_label_dict()

    label_to_region = dict(zip(params["numeric_label"], params["label_names"]))
    results = []
    for _, row in df_seg.iterrows():
        region = label_to_region[row["label"]]
        for metric_name in params["metrics_to_extract"]:
            if metric_name in row:
                value = row[metric_name]
                results.append({
                    "ID": params["subject_id"],
                    "region": region,
                    "metric": metric_name,
                    "value": float(value) if value is not None else float("nan"),
                    "model": params["model_name"]
                })

    df_metrics = pd.DataFrame(results)

    if cpu_cores == 1:
        return df_metrics

    # multiprocessing
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
                        "model_name": model_name
                    }

                    df_subject = process_subject_metricsreloaded(None, params, cpu_cores)
                    raw_metrics = pd.concat([raw_metrics, df_subject], ignore_index=True)

            logger.info(f"Finishing metric extraction for model {model_name}")

    else:
        # multiprocessing >1
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
                        "model_name": model_name
                    }

                    tasks.append(pool.apply_async(process_subject_metricsreloaded,
                                                  args=(shared_data, params, cpu_cores)))

                with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                    for task in tasks:
                        task.wait()
                        pbar.update(1)

                for subject_id, df_subject in shared_data.items():
                    raw_metrics = pd.concat([raw_metrics, df_subject], ignore_index=True)
                shared_data.clear()

                logger.info(f"Finishing metric extraction for model {model_name}")

    raw_metrics =  raw_metrics.sort_values(by=["model", "ID", "region"], ascending=[True, True, True])
    return raw_metrics.pivot_table(
                index=["ID", "region", "model"],
                columns="metric",
                values="value"
            ).reset_index()