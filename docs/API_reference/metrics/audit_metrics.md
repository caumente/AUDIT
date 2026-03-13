[//]: # (::: src.metric_extraction)

# AUDIT Custom Metrics

The **AUDIT backend (`backend: "audit"`)** computes a variety of native metrics to evaluate the performance of a segmentation model in relation to a ground truth reference. These metrics provide insights into the model's accuracy, overlap, and shape conformity with the actual segmented regions.

Below is an overview of each metric supported by the custom AUDIT extractor.

---

## Overlap Metrics

### 1. Dice Score (DICE)

The Dice Score Coefficient (DSC) is a measure of spatial overlap between the ground truth and the predicted segmentation. It ranges from 0 to 1, with 1 indicating perfect overlap.

$$ \text{Dice} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN} $$

Where $TP$ is true positives, $FP$ is false positives, and $FN$ is false negatives.

**Interpretation:** A higher Dice score indicates better agreement between the model's prediction and the ground truth. It is the most common metric for medical segmentation.

### 2. Jaccard Index (JACC)

Also known as the Intersection over Union (IoU), the Jaccard index is a stricter overlap-based metric. It measures the size of the intersection divided by the size of the union of the predicted and ground truth regions.

$$ \text{Jaccard} = \frac{TP}{TP + FP + FN} $$ 

**Interpretation:** A higher Jaccard index indicates a more accurate segmentation. Because it penalizes errors more heavily than Dice, it is always lower than the Dice score for the same non-perfect segmentation.

---

## Classification Metrics

### 3. Sensitivity (SENS)

Sensitivity, also known as **Recall** or the True Positive Rate, measures the ability of the model to correctly identify all the positive regions (e.g., all tumor voxels in an image).

$$ \text{Sensitivity} = \frac{TP}{TP + FN} $$

**Interpretation:** A higher sensitivity value implies the model successfully detects positive regions. However, it does not account for oversegmentation (false positives).

### 4. Specificity (SPEC)

Specificity measures the model's ability to correctly identify negative regions (e.g., healthy background voxels).

$$ \text{Specificity} = \frac{TN}{TN + FP} $$

**Interpretation:** A higher specificity value means the model is good at ignoring areas that should not be segmented, though it does not account for undersegmentation (missing true positives).

### 5. Precision (PREC)

Precision, or the Positive Predictive Value (PPV), measures the proportion of predicted positive voxels that are *actually* positive in the ground truth.

$$ \text{Precision} = \frac{TP}{TP + FP} $$

**Interpretation:** A high precision value means that when the model predicts a region to be part of the target class, that prediction is highly likely to be correct. It penalizes oversegmentation heavily.

### 6. Accuracy (ACCU)

Accuracy provides an overall measure of how often the model makes correct predictions (both true positives and true negatives) across all voxels in the image.

$$ \text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} $$

**Interpretation:** While a high accuracy score reflects general prediction success, it can be deceiving in highly imbalanced datasets (e.g., small targets in a large background).

---

## Distance & Structural Metrics

### 7. Hausdorff Distance (HAUS)

The Hausdorff distance is a spatial shape-based metric. It computes the maximum distance from a point on the predicted segmentation boundary to the closest point on the ground truth boundary.

$$ \text{Hausdorff Distance} = \max_{a \in A} \min_{b \in B} d(a, b) $$

Where $A$ is the set of points on the predicted segmentation boundary, $B$ is the set of points on the ground truth boundary, and $d(a, b)$ is the Euclidean distance between points.

**Interpretation:** Lower Hausdorff distances indicate that the furthest outlier boundary of the predicted segmentation is physically close to the ground truth boundary, implying better overall shape similarity.

### 8. Segmentation Size (SIZE)

This physical metric calculates the absolute size of the predicted segmentation, adjusted by the image's coordinate spacing to provide an accurate physical volume measurement.

$$ \text{Size} = (\text{Voxel count of predicted region}) \times (\text{Voxel Spacing}) $$

**Interpretation:** Allows researchers to quantify the total predicted target volume, which can be clinically relevant and compared directly against the expected physical volume from the ground truth.
