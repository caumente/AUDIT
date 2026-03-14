[//]: # (::: src.metric_extraction)

This `metric_extraction` pipeline processes medical image segmentation data by comparing ground truth segmentations with model 
predictions to compute a variety of evaluation metrics. 

Following a modular architecture, the pipeline supports multiple independent backends for metrics computation:
**AUDIT Custom Metrics**, **pymia**, and **Metrics Reloaded**.

The main entry point for the pipeline is `metric_extraction.py`, which routes the request to the appropriate decoupled backend located in `audit/metrics/backends/`.

## Pipeline Workflow

1. **Configuration & Setup**: The pipeline begins by loading a configuration file (`config.yaml`), which defines the dataset paths, 
the list of model predictions to evaluate, the specific metrics to calculate, and the chosen execution backend. Logging is automatically configured to track processing progress.

2. **Metric Extraction**: Depending on the `backend` specified in the configuration, the pipeline routes processing to one of three dedicated modules:

    *   **AUDIT Custom Metrics (`backend: "audit"`)**: Calculates specific metrics like Dice coefficient, Sensitivity, Hausdorff Distance, etc., based on 
    native implementations optimized for this project. Developers can add new custom metrics directly to this backend.
    *   **pymia (`backend: "pymia"`)**: Utilizes the popular [Pymia](https://github.com/rundherum/pymia) library's evaluation tools for medical image analysis. It natively supports confidence intervals and statistical aggregation during processing.
    *   **Metrics Reloaded (`backend: "metricsreloaded"`)**: Delegates computation to the [Metrics Reloaded project](https://github.com/Project-MONAI/MetricsReloaded), which offers a comprehensive suite of rigorously validated medical imaging metrics.

3. **Data Handling & Processing**: For the chosen dataset, metrics are computed across all specified models and all subjects. A shared utilities module (`audit/metrics/backends/commons.py`) ensures that NIfTI loading and multiprocessing execution remain consistent across all three backends.

4. **Structured Output**: Before returning results, the pipeline guarantees a standardized output shape via a shared contract. Regardless of which backend computes the metrics, the resulting `.csv` file will always have the following structural format:
    *   Rows are sorted by: `model` → `ID` (subject) → `region`
    *   Columns are ordered horizontally: `ID`, `region`, `model`, followed by the requested metrics sorted alphabetically.

This decoupled pipeline provides a flexible and scalable solution for evaluating segmentation models, allowing researchers to easily switch between evaluation frameworks while maintaining a consistent and comparable output format across their experiments.
