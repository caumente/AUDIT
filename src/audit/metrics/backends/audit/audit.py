import pandas as pd
from colorama import Fore
from loguru import logger

from audit.metrics.backends.commons import check_multiprocessing
from audit.metrics.backends.commons import initializer
from audit.metrics.backends.commons import load_subject_data
from audit.metrics.backends.commons import standardize_output
from audit.metrics.segmentation_metrics import calculate_metrics
from audit.metrics.segmentation_metrics import one_hot_encoding
from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_print
from audit.utils.commons.strings import fancy_tqdm
from multiprocessing import Lock
from multiprocessing import Manager
from multiprocessing import Pool


def process_subject(data: pd.DataFrame, params: dict, cpu_cores: int) -> pd.DataFrame:
    """Compute AUDIT custom metrics for a single subject."""
    path_ground_truth_dataset = params["path_ground_truth_dataset"]
    path_predictions = params["path_predictions"]
    numeric_label = params["numeric_label"]
    subject_id = params["subject_id"]
    label_names = params["label_names"]
    metrics_to_extract = params["metrics_to_extract"]
    model_name = params["model_name"]

    # load arrays using the shared utility
    gt, pred, spacing = load_subject_data(path_ground_truth_dataset, path_predictions, subject_id)

    # one-hot encode each region
    gt = one_hot_encoding(gt, numeric_label)
    pred = one_hot_encoding(pred, numeric_label)

    # compute metrics
    metrics = calculate_metrics(
        ground_truth=gt,
        segmentation=pred,
        subject=subject_id,
        regions=label_names,
        metrics=metrics_to_extract,
        spacing=spacing,
    )

    subject_info_df = pd.DataFrame(metrics)
    subject_info_df["model"] = model_name

    if cpu_cores == 1:
        return subject_info_df

    with dataframe_lock:
        data[subject_id] = subject_info_df

    return data


def extract_audit_metrics(config_file) -> pd.DataFrame:
    label_names = list(config_file["labels"].keys())
    numeric_label = list(config_file["labels"].values())

    path_ground_truth_dataset = config_file["data_path"]
    metrics_to_extract = [key for key, value in config_file["metrics"].items() if value]
    subjects_list = list_dirs(path_ground_truth_dataset)

    models = config_file["model_predictions_paths"]
    raw_metrics = pd.DataFrame()
    cpu_cores = check_multiprocessing(config_file)

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

                    subject_info_df = process_subject(pd.DataFrame(), params, cpu_cores)
                    raw_metrics = pd.concat([raw_metrics, subject_info_df], ignore_index=True)

            logger.info(f"Finishing metric extraction for model {model_name}")

        return standardize_output(raw_metrics)

    # multiprocessing path
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
                tasks.append(pool.apply_async(process_subject, args=(shared_data, params, cpu_cores)))

            with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                for task in tasks:
                    task.wait()
                    pbar.update(1)

            for subject_id, subject_info_df in shared_data.items():
                raw_metrics = pd.concat([raw_metrics, subject_info_df], ignore_index=True)

            logger.info(f"Finishing metric extraction for model {model_name}")

    return standardize_output(raw_metrics)
