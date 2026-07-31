# Metric availability by backend

Metric configuration keys are backend-specific. Each cell contains the exact
key to place under `metrics` in the YAML file. An em dash means that the backend
does not expose that metric.

| Metric | AUDIT | pymia | Metrics Reloaded |
|---|---|---|---|
| Dice coefficient | `dice` | `dice` | `dsc` |
| Jaccard / Intersection over Union | `jaccard` | `jacc` | `iou` |
| Accuracy | `accuracy` | `accu` | `accuracy` |
| Precision / Positive Predictive Value | `precision` | `prec` | `ppv` |
| Sensitivity / Recall | `sensitivity` | `sens` | `sensitivity` |
| Specificity | `specificity` | `spec` | `specificity` |
| Hausdorff distance (maximum) | `hausdorff_distance` | `haus` | `hd` |
| Predicted physical area/volume | `predicted_size` | `pred_vol` | — |
| Reference physical area/volume | — | `ref_vol` | — |
| Number of predicted pixels/voxels | — | — | `numb_pred` |
| Number of reference pixels/voxels | — | — | `numb_ref` |
| True positives | — | `tp` | `numb_tp` |
| False positives | — | `fp` | `numb_fp` |
| False negatives | — | `fn` | `numb_fn` |
| True negatives | — | `tn` | — |
| F-measure / F-beta | — | `fmeas` | `fbeta` |
| Cohen's kappa | — | `ckc` | `cohens_kappa` |
| Adjusted Rand Index | — | `ari` | — |
| Area Under Curve | — | `auc` | — |
| Interclass Correlation | — | `ic` | — |
| Mutual Information | — | `mi` | — |
| Rand Index | — | `rand` | — |
| Surface Dice Overlap | — | `sdo` | — |
| Surface Overlap | — | `so` | — |
| Volume Similarity | — | `vs` | — |
| Average Distance | — | `avd` | — |
| Mahalanobis Distance | — | `mahal` | — |
| Variation of Information | — | `vi` | — |
| Global Consistency Error | — | `gce` | — |
| Probabilistic Distance | — | `prob` | — |
| Fallout | — | `fallout` | — |
| False Negative Rate | — | `fnr` | — |
| Balanced Accuracy | — | — | `ba` |
| Weighted Cohen's Kappa | — | — | `wck` |
| Positive Likelihood Ratio | — | — | `lr+` |
| Youden Index | — | — | `youden_ind` |
| Negative Predictive Value | — | — | `npv` |
| Intersection over Reference | — | — | `ior` |
| Matthews Correlation Coefficient | — | — | `mcc` |
| Net Benefit | — | — | `nb` |
| Normalised Expected Cost | — | — | `ec` |
| Centreline Dice | — | — | `cldice` |
| Average Symmetric Surface Distance | — | — | `assd` |
| Mean Average Surface Distance | — | — | `masd` |
| Hausdorff Distance Percentile | — | — | `hd_perc` |
| Normalized Surface Distance | — | — | `nsd` |
| Boundary IoU | — | — | `boundary_iou` |
| Absolute Volume Difference Ratio | — | — | `avdr` |

`predicted_size` and `pred_vol` include image spacing. `numb_pred` is a raw
pixel/voxel count, so these values coincide only when the spacing product is
one.

pymia's `avd`, Metrics Reloaded's `assd`, and `masd` are shown on separate rows
because their surface-distance definitions are not interchangeable.

Metrics Reloaded also implements probability, calibration, detection, and
instance-segmentation metrics. They are not marked as available because AUDIT's
current metric pipeline accepts discrete segmentation masks, not the
probability maps or instance assignments those metric families require.
