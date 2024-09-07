from pathlib import Path
from datetime import datetime

import pandas as pd
from colorama import Fore
from loguru import logger
from pprint import pformat

from src.metrics.custom_metrics import calculate_metrics
from src.metrics.custom_metrics import one_hot_encoding
from src.utils.operations.file_operations import load_config_file
from src.utils.operations.file_operations import ls_dirs
from src.utils.operations.misc_operations import fancy_print
from src.utils.operations.misc_operations import fancy_tqdm
from src.utils.sequences import get_spacing
from src.utils.sequences import load_nii_by_id
from src.utils.operations.misc_operations import configure_logging


@logger.catch
def extract_metrics(config) -> pd.DataFrame:
    # load paths to test data
    path_test_dataset = config["data_path"]
    patients_list = ls_dirs(path_test_dataset)

    # initializing output metrics
    raw_metrics = pd.DataFrame()

    # load paths to predictions
    models = config["model_predictions_paths"]
    for model_name, path_predictions in models.items():
        fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
        logger.info(f"Starting metric extraction for model {model_name}")

        # loop over all the elements in the root folder
        with fancy_tqdm(total=len(patients_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
            for n, ID in enumerate(patients_list):
                pbar.set_postfix_str(f"{Fore.CYAN}Current patient: {Fore.LIGHTBLUE_EX}{ID}{Fore.CYAN}")
                pbar.update(1)
                if n % 10 == 0 and n > 0:
                    fancy_print(f"Processed {n} patients", Fore.CYAN, "🔹")

                # read ground truth segmentation and prediction
                gt = load_nii_by_id(root=path_test_dataset, patient_id=ID, as_array=True)
                pred = load_nii_by_id(root=path_predictions, patient_id=ID, seq="_pred", as_array=True)
                spacing = get_spacing(load_nii_by_id(path_predictions, ID, seq="_pred"))

                # making the segmentations binary (one hot encoding for each region)
                gt = one_hot_encoding(gt, numeric_label)
                pred = one_hot_encoding(pred, numeric_label)

                # compute metrics
                metrics = calculate_metrics(
                    ground_truth=gt, segmentation=pred, patient=ID, regions=label_names, spacing=spacing,
                )

                # from list of dict to dataframe
                patient_info_df = pd.DataFrame(metrics)

                # add model info
                patient_info_df["model"] = model_name

                # Add info to the main df
                raw_metrics = pd.concat([raw_metrics, patient_info_df], ignore_index=True)

        logger.info(f"Finishing metric extraction for model {model_name}")

    return raw_metrics


if __name__ == "__main__":
    logger.remove()
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    configure_logging(log_filename=f"./logs/metric_extraction/{current_time}.log")
    logger.info("Starting metric extraction process")

    # config variables
    config = load_config_file("./src/configs/metric_extractor.yml")
    label_names, numeric_label = (
        list(config["labels"].keys()),
        list(config["labels"].values()),
    )
    output_path = config["output_path"]
    Path(output_path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Config file: \n{pformat(config)}")

    extracted_metrics = extract_metrics(config=config)
    logger.info(f"Finishing metric extraction")

    # saving raw results
    extracted_metrics.to_csv(f"{output_path}/extracted_information_{config['filename']}.csv", index=False)
    logger.info(f"Results exported to CSV file")
