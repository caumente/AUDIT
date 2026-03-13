[//]: # (::: src.metric_extraction)

When the pipeline is configured to use the **`pymia` backend (`backend: "pymia"`)**, segmentation evaluation is 
delegated to the robust [pymia image analysis library](https://pymia.readthedocs.io/en/latest/).

References:

- [Jungo, Alain and Scheidegger, Olivier and Reyes, Mauricio and Balsiger, Fabian. pymia: A Python package for data handling and evaluation in deep learning-based medical image analysis. Computer Methods and Programs in Biomedicine
Volume 198, January 2021, 105796](https://doi.org/10.1016/j.cmpb.2020.105796)



Below is an outline of the metrics currently mapped and supported by this project's `pymia` wrapper, including their exact configuration keys.

## Supported metrics configuration

To extract these metrics, use the exact `Attribute name` under the `metrics` section of your configuration file.

| Metric Name                     | Attribute Name (Config) |
|---------------------------------|-------------------------|
| Dice Coefficient                | `dice`                  |
| Jaccard Coefficient (IoU)       | `jacc`                  |
| Sensitivity (Recall)            | `sens`                  |
| Specificity                     | `spec`                  |
| Precision (PPV)                 | `prec`                  |
| Accuracy                        | `accu`                  |
| False Negative Rate             | `fnr`                   |
| Area Under Curve (AUC)          | `auc`                   |
| Hausdorff Distance (100th %ile) | `haus`                  |

---

## Dice Coefficient (`dice`)
The Dice Coefficient (DSC) is a statistical tool measuring the spatial overlap between the prediction and reference.  
**Interpretation:** Values range from 0 (no overlap) to 1 (perfect overlap). It is identical to the F1 score.

---

## Jaccard Coefficient (`jacc`)
Commonly known as Intersection over Union (IoU), this measures the similarity and diversity of sample sets.  
**Interpretation:** Values range from 0 to 1. It is typically lower and stricter than the Dice Coefficient.

---

## Sensitivity / Recall (`sens`)
Evaluates the proportion of actual positive voxels that were correctly identified.  
**Interpretation:** High sensitivity means few false negatives (little undersegmentation). 

---

## Specificity (`spec`)
Evaluates the proportion of actual negative voxels that are correctly identified.  
**Interpretation:** High specificity means few false positives in the background areas.

---

## Precision (`prec`)
Measures the proportion of positively predicted voxels that actually belong to the target class.  
**Interpretation:** High precision means the model rarely oversegments outside the true target region.

---

## Accuracy (`accu`)
The ratio of correctly predicted observations (both true positives and true negatives) to the total observations.  
**Interpretation:** Useful for balanced datasets, but less meaningful if the target object is very small compared to the background.

---

## False Negative Rate (`fnr`)
The proportion of positive voxels that yield negative test outcomes with the model.  
**Interpretation:** Also known as the miss rate. Lower is better. ($FNR = 1 - \text{Sensitivity}$)

---

## Area Under Curve (`auc`)
Computes the Area Under the Receiver Operating Characteristic Curve (ROC-AUC) for the binary voxel-wise classification.  
**Interpretation:** Represents the degree or measure of separability; a higher AUC indicates the model is better at distinguishing between the regions.

---

## Hausdorff Distance (`haus`)
Evaluates the maximum spatial distance between the boundary of the prediction and the boundary of the ground truth. The implementation in this backend utilizes the 100th percentile (the true mathematical maximum distance).  
**Interpretation:** Lower values indicate that the predicted boundary tightly follows the true boundary without any severe outlier errors.