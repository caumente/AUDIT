import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from pathlib import Path
from pprint import pformat

from colorama import Fore
from loguru import logger

from src.features.main import extract_features
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.strings import configure_logging
from src.utils.commons.strings import fancy_print

if __name__ == "__main__":
    logger.remove()
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    configure_logging(log_filename=f"./logs/feature_extraction/{current_time}.log")
    logger.info("Starting feature extraction process")

    # config variables
    config = load_config_file("./src/configs/feature_extractor.yml")
    data_paths = config["data_paths"]
    output_path = config["output_path"]
    Path(output_path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Config file: \n{pformat(config)}")

    # iterate over all paths
    for dataset_name, src_path in data_paths.items():
        fancy_print(f"Starting feature extraction for {dataset_name}", Fore.LIGHTMAGENTA_EX, "\n✨")
        logger.info(f"Starting feature extraction for {dataset_name}")

        # features extraction
        extracted_feats = extract_features(path_images=src_path, config_file=config, dataset_name=dataset_name)
        logger.info(f"Finishing feature extraction for {dataset_name}")

        # TODO: Should it have nan values or they must be 0? When NAN value, they do not appear in plots.
        extracted_feats.to_csv(f"{output_path}/extracted_information_{dataset_name}.csv", index=False)
        logger.info(f"Results exported to CSV for {dataset_name}")
