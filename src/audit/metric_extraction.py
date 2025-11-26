import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from pathlib import Path
from pprint import pformat

import pandas as pd
from loguru import logger

from audit.metrics.main import extract_audit_metrics
from audit.metrics.main import extract_pymia_metrics
from audit.utils.internal._config_helpers import check_metric_extraction_config
from audit.utils.internal._config_helpers import configure_logging
from audit.utils.internal._config_helpers import load_config_file


def run_metric_extraction(config_path):
    # Load the configuration file
    try:
        config = load_config_file(config_path)
    except Exception as e:
        logger.error(f"Failed to load config file from {config_path}: {e}")
        sys.exit(1)

    check_metric_extraction_config(config)

    # config variables
    output_path, logs_path = config["output_path"], config["logs_path"]
    Path(output_path).mkdir(parents=True, exist_ok=True)
    Path(logs_path).mkdir(parents=True, exist_ok=True)

    # initializing log
    logger.remove()
    if config.get("logger", None):
        logger.add(sink=sys.stdout, level=config["logger"])
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    configure_logging(log_filename=f"{logs_path}/{current_time}.log")
    logger.info(f"Config file: \n{pformat(config)}")
    logger.info("Starting metric extraction process")

    if config["package"] == "audit":
        extracted_metrics = extract_audit_metrics(config_file=config)
    elif config["package"] == "pymia":
        extracted_metrics = extract_pymia_metrics(config_file=config)
    else:
        extracted_metrics = pd.DataFrame()

    logger.info(f"Finishing metric extraction")

    # store information
    if not extracted_metrics.empty:
        file_path = os.path.join(output_path, f"extracted_information_{config['filename']}.csv")
        extracted_metrics.to_csv(file_path, index=False)
        logger.info(f"Results exported to CSV file")


def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Metric extraction for AUDIT.")
    parser.add_argument(
        "--config",
        type=str,
        default="./configs/metric_extraction.yml",  # Path relative to the script location
        help="Path to the configuration file for metric extraction (default is './configs/metric_extraction.yml').",
    )
    args = parser.parse_args()

    run_metric_extraction(args.config)


if __name__ == "__main__":
    main()
