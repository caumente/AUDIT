import os
import re
import sys
from pathlib import Path

import yaml
from loguru import logger


def load_config_file(path: str) -> dict:
    """
    Loads a configuration file in YAML format and returns its contents as a dictionary.

    Args:
        path: The relative file root_dir to the YAML configuration file.

    Returns:
        dict: The contents of the YAML file as a dictionary.
    """

    def replace_variables(config, variables):
        def replace(match):
            return variables.get(match.group(1), match.group(0))

        for key, value in config.items():
            if isinstance(value, str):
                config[key] = re.sub(r"\$\{(\w+)\}", replace, value)
            elif isinstance(value, dict):
                replace_variables(value, variables)

    # Resolve the absolute root_dir based on the current file's path
    base_dir = Path(__file__).resolve().parent.parent.parent  # Adjust the depth according to your project
    absolute_path = base_dir / path

    # Validate if the file exists
    if not absolute_path.exists():
        raise FileNotFoundError(f"Config file not found: {absolute_path}")

    # Load the YAML file
    with open(absolute_path, "r") as file:
        config = yaml.safe_load(file)

    # Replace variables in the YAML configuration
    variables = {key: value for key, value in config.items() if not isinstance(value, dict)}
    replace_variables(config, variables)

    return config


def init_app_yaml(dest: Path):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    yaml_content = """\
# Sequences available. First of them will be used to compute properties like spacing
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# Root paths
datasets_path: './datasets'
features_path: './outputs/features'
metrics_path: './outputs/metrics'

# Paths for raw datasets
raw_datasets:
  dataset_1: "${datasets_path}/dataset_1/images"
  dataset_2: "${datasets_path}/dataset_2/images"

# Paths for feature extraction CSV files
features:
  dataset_1: "${features_path}/dataset_1.csv"
  dataset_2: "${features_path}/dataset_2.csv"

# Paths for metric extraction CSV files
metrics:
  dataset_1: "${metrics_path}/dataset_1.csv"
  dataset_2: "${metrics_path}/dataset_2.csv"

# Paths for model predictions
predictions:
  dataset_1:
    modelA: "${datasets_path}/dataset_1/seg/modelA"
    modelB: "${datasets_path}/dataset_1/seg/modelB"
  dataset_2:
    modelA: "${datasets_path}/dataset_2/seg/modelA"
    modelB: "${datasets_path}/dataset_2/seg/modelB"
"""
    with open(dest, "w") as f:
        f.write(yaml_content)


def init_feature_extraction_yaml(dest: Path):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    yaml_content = """\
# Paths to all the datasets
data_paths:
  dataset_1: '/path/to/dataset_1/images'
  dataset_2: '/path/to/dataset_2/images'

# Sequences available
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# List of features to extract
features:
  statistical: true
  texture: true
  spatial: true
  tumor: true

# Longitudinal study settings
longitudinal:
  dataset_2:
    pattern: "_"
    longitudinal_id: 1
    time_point: 2

# Path where extracted features will be saved
output_path: './outputs/features'
logs_path: './logs/features'

# Other settings
cpu_cores: 8
"""
    with open(dest, "w") as f:
        f.write(yaml_content)


def init_metric_extraction_yaml(dest: Path):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    yaml_content = """\
# Path to the raw dataset
data_path: '/path/to/dataset_2/images'

# Paths to model predictions
model_predictions_paths:
  modelA: '/path/to/dataset_2/seg/modelA'
  modelB: '/path/to/dataset_2/seg/modelB'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# List of metrics to compute
metrics:
  dice: true
  jacc: true
  accu: true
  prec: true
  sens: true
  spec: true
  haus: true
  size: true

# Library used for computing all the metrics
package: audit

# Path where output metrics will be saved
output_path: './outputs/metrics'
filename: 'dataset_2'
logs_path: './logs/metric'

# Other settings
cpu_cores: 12
"""
    with open(dest, "w") as f:
        f.write(yaml_content)


def check_path_access(path: str, name: str) -> None:
    """Check if the path exists and the user has access to it."""
    try:
        os.makedirs(path, exist_ok=True)
    except (PermissionError, FileNotFoundError, OSError) as _:
        logger.error(f"Cannot access {name}: {path}")
        sys.exit(1)


def check_path_existence(path: str, name: str, group_1: str = None, group_2: str = None) -> None:
    """Check if the path exists."""
    group_1 = f"{group_1}: " if group_1 is not None else ""
    group_2 = f"{group_2}: " if group_2 is not None else ""
    if not os.path.exists(path):
        logger.error(f"Unresolved path for {group_2}{group_1}{name}: {path}")
        sys.exit(1)


def check_feature_extraction_config(config: dict) -> None:
    """Check the configuration for the feature extraction."""
    # check input data
    data_paths = config.get("data_paths")
    if data_paths is None:
        logger.error("Missing data_paths in the feature_extraction.yml file")
        sys.exit(1)
    for dataset_name, src_path in data_paths.items():
        check_path_existence(src_path, dataset_name, "data_paths")

    # check feature extraction outputs
    output_path = config.get("output_path")
    if output_path is None:
        logger.error("Missing output_path in the feature_extraction.yml file")
        sys.exit(1)
    check_path_access(config.get("output_path"), "output_path")

    # logs outputs
    logs_path = config.get("logs_path")
    if logs_path is None:
        logger.error("Missing logs_path in the feature_extraction.yml file")
        sys.exit(1)
    check_path_access(config.get("logs_path"), "logs_path")

    # Ensure features, labels, and sequences are not empty
    if not config.get("features"):
        logger.error("Missing features key in the feature_extraction.yml file")
        sys.exit(1)

    if not config.get("labels"):
        logger.error("Missing labels key in the feature_extraction.yml file")
        sys.exit(1)

    if not config.get("sequences"):
        logger.error("Missing sequences key in the feature_extraction.yml file")
        sys.exit(1)


def check_metric_extraction_config(config: dict) -> None:
    """Check the configuration for the metric extraction."""
    # check input data
    data_path = config.get("data_path")
    if data_path is None:
        logger.error("Missing data_path in the metric_extraction.yml file")
        sys.exit(1)
    check_path_existence(data_path, "data_path")

    # check model predictions
    model_predictions_paths = config.get("model_predictions_paths")
    if model_predictions_paths is None:
        logger.error("Missing model_predictions_paths in the metric_extraction.yml file")
        sys.exit(1)
    for model_name, path_predictions in model_predictions_paths.items():
        check_path_existence(path_predictions, model_name, "model_predictions_paths")

    # check feature extraction outputs
    output_path = config.get("output_path")
    if output_path is None:
        logger.error("Missing output_path in the metric_extraction.yml file")
        sys.exit(1)
    check_path_access(config.get("output_path"), "output_path")

    # log outputs
    logs_path = config.get("logs_path")
    if logs_path is None:
        logger.error("Missing logs_path in the metric_extraction.yml file")
        sys.exit(1)
    check_path_access(config.get("logs_path"), "logs_path")

    # Ensure metrics, labels, filename, and package are not empty
    if not config.get("labels"):
        logger.error("Missing labels key in the metric_extraction.yml file")
        sys.exit(1)

    if not config.get("metrics"):
        logger.error("Missing metrics key in the metric_extraction.yml file")
        sys.exit(1)

    if not config.get("package"):
        logger.error("Missing package key in the metric_extraction.yml file")
        sys.exit(1)

    if not config.get("filename"):
        logger.error("Missing filename key in the metric_extraction.yml file")
        sys.exit(1)


def check_app_config(config: dict) -> None:
    """Check the configuration for the app."""
    raw_datasets = config.get("raw_datasets")
    if raw_datasets is not None:
        for dataset_name, src_path in raw_datasets.items():
            if dataset_name is None or src_path is None:
                logger.error(f"Not set features: {dataset_name}: {src_path} in the app.yml file")
                sys.exit(1)
            check_path_existence(src_path, dataset_name, "raw_datasets")

    features = config.get("features")
    if features is not None:
        for feature_name, src_path in features.items():
            if feature_name is None or src_path is None:
                logger.error(f"Not set features: {features}: {src_path} in the app.yml file")
                sys.exit(1)
            check_path_existence(src_path, feature_name, "features")

    metrics = config.get("metrics")
    if metrics is not None:
        for metric_name, src_path in metrics.items():
            if metric_name is None or src_path is None:
                logger.error(f"Not set metrics: {metric_name}: {src_path} in the app.yml file")
                sys.exit(1)
            check_path_existence(src_path, metric_name, "metrics")

    predictions = config.get("predictions")
    if predictions is not None:
        for dataset_name in predictions.keys():
            if predictions[dataset_name] is None:
                logger.error(f"Not set predictions: {dataset_name}: None in the app.yml file")
                sys.exit(1)
            for prediction_name, src_path in predictions[dataset_name].items():
                if prediction_name is None or src_path is None:
                    logger.error(
                        f"Not set predictions: {dataset_name}: {prediction_name}: {src_path} in the app.yml file"
                    )
                    sys.exit(1)
                check_path_existence(src_path, prediction_name, dataset_name, "predictions")

    # Ensure features, labels, and sequences are not empty
    if not config.get("labels"):
        logger.error("Missing labels key in the feature_extraction.yml file")
        sys.exit(1)

    if not config.get("sequences"):
        logger.error("Missing sequences key in the feature_extraction.yml file")
        sys.exit(1)


def configure_logging(log_filename: str):
    logger.add(log_filename, retention="90 days", level="INFO")
