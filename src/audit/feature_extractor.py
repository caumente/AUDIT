import os
import sys
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from pathlib import Path
from pprint import pformat

from colorama import Fore
from loguru import logger

from audit.features.main import extract_features
from audit.utils.commons.file_manager import load_config_file
from audit.utils.commons.strings import configure_logging
from audit.utils.commons.strings import fancy_print


def run_feature_extractor(config_path):
    # Load the configuration file
    try:
        config = load_config_file(config_path)
    except Exception as e:
        logger.error(f"Failed to load config file from {config_path}: {e}")
        sys.exit(1)

    # config variables
    data_paths = config["data_paths"]
    output_path, logs_path = config["output_path"], config["logs_path"]
    Path(output_path).mkdir(parents=True, exist_ok=True)
    Path(logs_path).mkdir(parents=True, exist_ok=True)

    # initializing log
    logger.remove()
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    configure_logging(log_filename=f"{logs_path}/{current_time}.log")
    logger.info(f"Config file: \n{pformat(config)}")
    logger.info("Starting feature extraction process")

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


def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Feature extraction for AUDIT.")
    parser.add_argument(
        '--config',
        type=str,
        default='./configs/feature_extractor.yml',  # Path relative to the script location
        help="Path to the configuration file for feature extraction (default is './configs/feature_extractor.yml')."
    )
    args = parser.parse_args()

    run_feature_extractor(args.config)


if __name__ == "__main__":
    main()
