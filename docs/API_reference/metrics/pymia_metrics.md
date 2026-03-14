[//]: # (::: src.metric_extraction)


When the pipeline is configured to use the **`pymia` backend (`backend: "pymia"`)**, segmentation evaluation is 
delegated to the robust [pymia image analysis library](https://pymia.readthedocs.io/en/latest/).

References:

- [Jungo, Alain and Scheidegger, Olivier and Reyes, Mauricio and Balsiger, Fabian. pymia: A Python package for data handling and evaluation in deep learning-based medical image analysis. Computer Methods and Programs in Biomedicine
Volume 198, January 2021, 105796](https://doi.org/10.1016/j.cmpb.2020.105796)

  
Below is an outline of the metrics currently mapped and supported by this project's `pymia` wrapper, including their 
exact configuration keys. It is important to note that not all metrics provided by `pymia` are necessarily meaningful 
or commonly used in the context of segmentation evaluation. The pymia library exposes a broad set of evaluation 
measures, some of which are designed for more general machine learning or statistical comparison tasks. Nevertheless, 
for completeness and flexibility, the wrapper implemented in `AUDIT` exposes most of the metrics currently supported by pymia, 
allowing users to select those that best fit their specific evaluation needs.

## Supported metrics configuration

To extract these metrics, use the exact `Attribute name` under the `metrics` section of your configuration file.

### Overlap Metrics

| Metric Name                     | Attribute Name (Config) |
|---------------------------------|-------------------------|
| Adjusted Rand Index             | `ari`                   |
| Area Under Curve (AUC)          | `auc`                   |
| Cohen Kappa Coefficient         | `ckc`                   |
| Dice Coefficient                | `dice`                  |
| Interclass Correlation          | `ic`                    |
| Jaccard Coefficient (IoU)       | `jacc`                  |
| Mutual Information              | `mi`                    |
| Rand Index                      | `rand`                  |
| Surface Dice Overlap            | `sdo`                   |
| Surface Overlap                 | `so`                    |
| Volume Similarity               | `vs`                    |

### Distance Metrics
| Metric Name                     | Attribute Name (Config) |
|---------------------------------|-------------------------|
| Average Distance                | `avd`                   |
| Global Consistency Error        | `gce`                   |
| Hausdorff Distance (100th %ile) | `haus`                  |
| Mahalanobis Distance            | `mahal`                 |
| Probabilistic Distance          | `prob`                  |
| Variation Of Information        | `vi`                    |

### Classical Metrics
| Metric Name                     | Attribute Name (Config) |
|---------------------------------|-------------------------|
| Accuracy                        | `accu`                  |
| Fallout                         | `fallout`               |
| F-Measure                       | `fmeas`                 |
| False Negative Count            | `fn`                    |
| False Negative Rate             | `fnr`                   |
| False Positive Count            | `fp`                    |
| Precision (PPV)                 | `prec`                  |
| Prediction Volume               | `pred_vol`              |
| Reference Volume                | `ref_vol`               |
| Sensitivity (Recall)            | `sens`                  |
| Specificity                     | `spec`                  |
| True Negative Count             | `tn`                    |
| True Positive Count             | `tp`                    |


### Regression Metrics
| Metric Name                     | Attribute Name (Config) |
|---------------------------------|-------------------------|
| Coefficient Of Determination    | `cd`                    |
| Mean Absolute Error             | `mae`                   |
| Mean Squared Error              | `mse`                   |
| Root Mean Squared Error         | `rmse`                  |
| Normalized Root Mean Squared Error | `nrmse`              |

