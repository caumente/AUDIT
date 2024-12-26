[//]: # (::: src.metric_extractor)

# Metrics Computed

The provided code computes a variety of metrics to evaluate the performance of a segmentation model in relation to the 
ground truth. These metrics provide insights into the model's accuracy, overlap, and shape conformity with the actual 
segmented regions. Below is an overview of each metric computed:

## 1. Dice Score (DICE)

The Dice score (or Dice coefficient) is a measure of overlap between the ground truth and the predicted segmentation. It ranges from 0 to 1, with 1 indicating perfect overlap.

$$ \text{Dice} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN} $$

Where `TP` is true positives, `FP` is false positives, and `FN` is false negatives.

Interpretation: A higher Dice score indicates better agreement between prediction and ground truth.

## 2. Jaccard Index (JACC)

Also known as the Intersection over Union (IoU), the Jaccard index is another overlap-based metric. It measures the 
size of the intersection divided by the size of the union of the predicted and ground truth regions.

$$ \text{Jaccard} = \frac{TP}{TP + FP + FN} $$ 

Interpretation: A higher Jaccard index indicates a more accurate segmentation. It is always lower than the Dice score 
for the same segmentation.

## 3. Sensitivity (SENS)

Sensitivity, also known as recall or true positive rate, measures the ability of the model to correctly identify all 
the positive regions (i.e., tumor voxels).

$$ \text{Sensitivity} = \frac{TP}{TP + FN} $$

Interpretation: A higher sensitivity value indicates the model is good at detecting positive regions (e.g., tumor 
regions), but it doesn’t account for false positives.

## 4. Specificity (SPEC)

Specificity measures the model's ability to correctly identify negative regions (i.e., non-tumor voxels).

$$ \text{Specificity} = \frac{TN}{TN + FP} $$

Interpretation: A higher specificity value indicates the model is good at ignoring false positives, but doesn’t account
for missing true positives.

## 5. Precision (PREC)

Precision, or positive predictive value, measures the proportion of predicted positive cases that are actually positive.

$$ \text{Precision} = \frac{TP}{TP + FP} $$

Interpretation: A high precision value means that when the model predicts a positive case (e.g., tumor), it is likely 
correct.

## 6. Accuracy (ACCU)

Accuracy provides an overall measure of how often the model makes correct predictions (both true positives and true 
negatives) across all regions.

$$ \text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} $$

Interpretation: A high accuracy score reflects the model’s general performance in predicting both positive and negative cases.

## 7. Hausdorff Distance (HAUS)

The Hausdorff distance is a shape-based metric that measures the maximum distance between points on the predicted 
segmentation and the corresponding points on the ground truth.

$$ \text{Hausdorff Distance} = \max_{x \in A} \min_{y \in B} d(x, y) $$

Where `A` is the set of points on the predicted segmentation, `B` is the set of points on the ground truth, and 
`d(x, y)` is the Euclidean distance between points.

Interpretation: Lower Hausdorff distances indicate that the boundary of the predicted segmentation is closer to the ground truth boundary, implying better shape similarity.

## 8. Segmentation Size (SIZE)

This metric calculates the physical size of the predicted segmentation in terms of voxel count, adjusted by the voxel spacing to provide a volume measurement.

$$ \text{Size} = \text{Voxel count of predicted region} \times \text{Spacing} $$

Interpretation: This helps to quantify the total volume of the segmented region, which can be compared to the expected 
size from the ground truth.
