[//]: # (::: src.metrics.main)


This `metric extraction` pipeline processes MRI segmentation data by comparing ground truth segmentations with model 
predictions to compute a variety of metrics. The pipeline supports several backend frameworks for metrics computation,
including custom AUDIT metrics, 
[Pymia](), and 
[Metrics Reloaded](https://github.com/Project-MONAI/MetricsReloaded), 
handling multiple model predictions and datasets. The two 
main components of the pipeline are metric_extraction.py, which serves as the entry point, and main.py, which contains 
the core logic for metric computation.

The pipeline operates as follows:

- **Configuration and Logging**: The pipeline begins by loading a configuration file, which defines the dataset paths, 
models, metrics to be extracted, and output settings. Logging is set up to track the progress and output detailed logs.

- **Metric Extraction**: Depending on the configuration, the pipeline can compute either custom metrics (using methods 
defined in the project), Pymia metrics (using the Pymia library for medical image analysis), or Metrics Reloaded project.
All evaluator process the predicted and reference segmentation volumes and output the computed metrics across 
subjects, models, and regions.

    - **Custom Metrics**: This approach calculates specific metrics like Dice coefficient, sensitivity, or others based on 
  custom implementations. Users can create their own metrics to extend AUDIT capabilities based on specific requirements.
  
    - **Pymia**: Here Pymia's built-in metrics are used for segmentation evaluation.

    - **Metrics Reloaded**: Here Metrics Reloaded built-in metrics are used for segmentation evaluation.


- **Data Processing**: For each dataset and model, metrics are computed for all subjects. The results are collected 
into a DataFrame, and if longitudinal data is involved, it can further organize the results by time points.

- **Output**: The extracted metrics are stored as CSV files. The output is structured and ready for 
further analysis or reporting.

This pipeline provides a flexible and scalable solution for evaluating segmentation models, making it suitable for 
multi-model comparisons and performance tracking across different datasets.

