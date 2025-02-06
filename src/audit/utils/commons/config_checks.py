import sys
import os
from loguru import logger


def check_path_access(path: str, name: str) -> None:
    """Check if the path exists and the user has access to it."""
    try:
        os.makedirs(path, exist_ok=True)
    except (PermissionError, FileNotFoundError, OSError) as _:
        logger.error(f'Cannot access {name}: {path}')
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
        for dataset_name  in predictions.keys():
            if predictions[dataset_name] is None:
                logger.error(f"Not set predictions: {dataset_name}: None in the app.yml file")
                sys.exit(1)
            for prediction_name, src_path in predictions[dataset_name].items():
                if prediction_name is None or src_path is None:
                    logger.error(f"Not set predictions: {dataset_name}: {prediction_name}: {src_path} in the app.yml file")
                    sys.exit(1)
                check_path_existence(src_path, prediction_name, dataset_name, "predictions")

    # Ensure features, labels, and sequences are not empty
    if not config.get("labels"):
        logger.error("Missing labels key in the feature_extraction.yml file")
        sys.exit(1)

    if not config.get("sequences"):
        logger.error("Missing sequences key in the feature_extraction.yml file")
        sys.exit(1)