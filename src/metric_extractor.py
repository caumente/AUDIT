import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from datetime import datetime

import pandas as pd
from loguru import logger
from pprint import pformat

from src.utils.operations.file_operations import load_config_file
from src.utils.operations.misc_operations import configure_logging
from src.metrics.main import extract_custom_metrics
from src.metrics.main import extract_pymia_metrics


if __name__ == "__main__":
    logger.remove()
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    configure_logging(log_filename=f"./logs/metric_extraction/{current_time}.log")
    logger.info("Starting metric extraction process")

    # config variables
    config = load_config_file("./src/configs/metric_extractor.yml")
    output_path = config["output_path"]
    Path(output_path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Config file: \n{pformat(config)}")

    if config["package"] == 'custom':
        extracted_metrics = extract_custom_metrics(config_file=config)
    elif config["package"] == 'pymia':
        extracted_metrics = extract_pymia_metrics(config_file=config)
    else:
        extracted_metrics = pd.DataFrame()

    logger.info(f"Finishing metric extraction")

    # store information
    extracted_metrics.to_csv(f"{output_path}/extracted_information_{config['filename']}.csv", index=False)
    logger.info(f"Results exported to CSV file")
