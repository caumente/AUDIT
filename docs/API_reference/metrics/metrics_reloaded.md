[//]: # (::: src.metric_extraction)


When the pipeline is configured to use the **Metrics Reloaded backend (`backend: "metricsreloaded"`)**, segmentation performance is evaluated using a comprehensive suite of rigorously validated metrics derived from pixel-wise classifications.
Although the Metrics Reloaded backend allows the computation of a wide range of metrics, some are more suitable than others 
for segmentation problems. To discover which metrics are most appropriate for a given task, please consult 
[Metrics Reloaded Metric Library](https://metrics-reloaded.dkfz.de/metric-library).

References:

- [Reinke, A., Tizabi, M.D., Baumgartner, M. et al. Understanding metric-related pitfalls in image analysis validation. Nat Methods 21, 182–194 (2024).](https://doi.org/10.1038/s41592-023-02150-0)

- [Maier-Hein, L., Reinke, A., Godau, P. et al. Metrics reloaded: recommendations for image analysis validation. Nat Methods 21, 195–212 (2024).](https://doi.org/10.1038/s41592-023-02151-z)

These metrics capture different aspects of segmentation quality, including overlap, and boundary agreement. 

## Supported metrics configuration

To extract these metrics, use the exact `Attribute name` under the `metrics` section of your configuration file.

| Metric name (Documentation)               | Attribute name (config file) |
|-------------------------------------------|------------------------------|
| Number of reference pixels                | numb_ref                     |
| Number of predicted pixels                | numb_pred                    |
| True positives                            | numb_tp                      |
| False positives                           | numb_fp                      |
| False negatives                           | numb_fn                      |
| Accuracy                                  | accuracy                     |
| Balanced Accuracy (BA)                    | ba                           |
| Sensitivity (Recall)                      | sensitivity                  |
| Specificity                               | specificity                  |
| Positive Predictive Value (PPV)           | ppv                          |
| Negative Predictive Value (NPV)           | npv                          |
| Intersection over Union (IoU)             | iou                          |
| F-beta score                              | fbeta                        |
| Dice Score Coefficient (DSC)              | dsc                          |
| Matthews Correlation Coefficient (MCC)    | mcc                          |
| Cohen's Kappa                             | cohens_kappa                 |
| Weighted Cohen's Kappa                    | wck                          |
| Positive Likelihood Ratio + (LR+)         | lr+                          |
| Net Benefit (NB)                          | nb                           |
| Normalised Expected Cost (ECn)            | ec                           |
| Centreline Dice (CL Dice)                 | cldice                       |
| Average Symmetric Surface Distance (ASSD) | assd                         |
| Mean Average Surface Distance (MASD)      | masd                         |
| Hausdorff Distance (HD)                   | hd                           |
| Hausdorff Distance Percentile (HD95)      | hd_perc                      |
| Normalized Surface Distance (NSD)         | nsd                          |
| Boundary IoU                              | boundary_iou                 |
| Intersection over Reference (IoR)         | ior                          |
| Absolute Volume Difference Ratio (AVDR)   | avdr                         |



## Counting metrics

### Dice Score Coefficient (DSC)

DSC measures the overlap between two structures.
Find more information about [DSC](https://metrics-reloaded.dkfz.de/metric-library/dsc).


$$ \text{DSC(A, B)} = \frac{2 |A \cap B|}{|A| + |B|} = \frac{2 \cdot \text{PPV} \cdot \text{Sensitivity}}{\text{PPV} + \text{Sensitivity}} $$ 


**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates perfect overlap.

---

### Intersection over Union (IoU)

Also known as Jaccard Index, IoU measures the overlap between two structures.
Find more information about [IoU](https://metrics-reloaded.dkfz.de/metric-library/intersection_over_union).

$$ \text{IoU}(\text{A}, \text{B}) = \frac{|\text{A} \cap \text{B}|}{|\text{A}| + |\text{B}| - |\text{A} \cap \text{B}|} = \frac{|\text{A} \cap \text{B}|}{|\text{A} \cup \text{B}|} $$

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates perfect overlap.

---

### F-Beta Score (Fβ)


The special case of β = 1 is the harmonic mean of PPV and Sensitivity and is a common metric in segmentation problems 
(here usually referred to as DSC). In segmentation problems, Fβ Score weights the penalization of oversegmentation (FP) 
and undersegmentation (FN) with the parameter β. 
Find more information about [Fβ](https://metrics-reloaded.dkfz.de/metric-library/f_beta).

$$ \text{F}_{\text{β}}\: \text{Score} = \frac{(1 + \text{β}^2) \cdot \text{PPV} \cdot \text{Sensitivity}}
        {\text{β}^2 \cdot \text{PPV} + \text{Sensitivity}} = \frac{(1 + \text{β}^2) \cdot \text{TP}}{(1 + \text{β}^2) \cdot \text{TP} +
        \text{β}^2 \cdot \text{FN} + \text{FP}} $$

When \( \beta = 1 \), the metric is equivalent to the Dice coefficient.

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates perfect overlap.

---

### Centreline Dice (CL Dice)

clDice measures the overlap between two structures, ideally tubular-shaped. The formula is similar to the DSC, but 
relies on the topology precision and topology sensitivity which are defined based on the skeletons of the structures. 
Find more information about [CL Dice](https://metrics-reloaded.dkfz.de/metric-library/cl_dice).

\[
cDSC =
2\frac{T_{sens} \cdot T_{prec}}{T_{sens} + T_{prec}}
\]

Where:

- \(T_{sens}\) is topology sensitivity
- \(T_{prec}\) is topology precision

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates perfect overlap.

---

### Intersection over Reference (IoR)

IoR measures the overlap between two structures. It is defined as the pixel-level Sensitivity and only considers the FN 
pixels (not the FPs).
Find more information about [IoR](https://metrics-reloaded.dkfz.de/metric-library/intersection_over_reference).

$$
\text{IoR(A, B)} = \frac{|\text{A} \cap \text{B}|}{|\text{A}|}
$$


**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates that the reference structure is fully covered by the prediction.

---

### Absolute Volume Difference Ratio (AVDR)

AVDR measures the relative difference between the predicted and reference volumes.

$$
\text{AVDR} =
\frac{|V_{pred} - V_{ref}|}{V_{ref}}
$$

**Interpretation:**  
Lower values indicate better agreement between predicted and reference volumes.

---

### Accuracy

Accuracy measures the ratio of samples that were correctly classified over all predictions made.
Find more information about [Accuracy](https://metrics-reloaded.dkfz.de/metric-library/accuracy).

$$ \text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}} $$ 

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates perfect classification.

---

### Balanced Accuracy (BA)

BA measures the arithmetic mean of Sensitivities for each class, i.e., for each class, it measures the fraction of 
actual positive samples that were predicted as such.
Find more information about [BA](https://metrics-reloaded.dkfz.de/metric-library/balanced_accuracy).

$$ \text{BA} = \frac{1}{2} \Biggl( \frac{\text{TP}}{\text{TP} + \text{FN}} + \frac{\text{TN}}{\text{TN} + \text{FP}} \Biggr) = \frac{1}{2} (\text{Sensitivity} + \text{Specificity}) $$


**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates perfect classification.

---

### Sensitivity (Recall)

Sensitivity measures how good a method is in classifying truly positive samples as positive.
Find more information about [CL Dice](https://metrics-reloaded.dkfz.de/metric-library/sensitivity).

$$ \text{Sensitivity} = \frac{\text{TP}}{\text{TP} + \text{FN}} $$

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates that all true positive samples were correctly classified.

---

### Specificity

Specificity measures how good a method is in classifying truly negative samples as negative. 
Find more information about [Specificity](https://metrics-reloaded.dkfz.de/metric-library/specificity).

$$ \text{Specificity} = \frac{\text{TN}}{\text{TN} + \text{FP}} $$

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates that all negative samples were correctly classified.

---

### Positive Predictive Value (PPV)

Also known as **Precision**, PPV represents the probability of a positive prediction corresponding to an actual positive sample.  
Find more information about [PPV](https://metrics-reloaded.dkfz.de/metric-library/PPV).

$$
\text{PPV}_{\text{corrected}} =\;
\frac{\text{Sensitivity} \cdot \text{Prevalence}}
{\text{Sensitivity} \cdot \text{Prevalence} \, + \, (1 - \text{Specificity}) \cdot (1 -\text{Prevalence})}
$$

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates that all predicted positive samples are correct.

---

### Negative Predictive Value (NPV)

NPV represents the probability of a negative prediction corresponding to an actual negative sample. 
Find more information about [NPV](https://metrics-reloaded.dkfz.de/metric-library/negative_predictive_value).

$$
\text{NPV} = \frac{\text{TN}}{\text{TN} + \text{FN}}, \;\;\; \small{\text{if prevalence = 0.5}}
$$

**Interpretation:**  
Values range from 0 to 1. A value of 1 indicates that all predicted negative samples are correct.

---

### Matthews Correlation Coefficient (MCC)

MCC measures the correlation between the actual and the predicted class.  
Find more information about [MCC](https://metrics-reloaded.dkfz.de/metric-library/matthews_correlation).

$$
\text{MCC} =\;
\frac{\text{TP} \cdot \text{TN} - \text{FP} \cdot \text{FN}}
{\sqrt{(\text{TP}+\text{FP})(\text{TP}+\text{FN})(\text{TN}+\text{FP})(\text{TN}+\text{FN})}}
$$

**Interpretation:**  
Values range from −1 to 1.

- 1 indicates perfect prediction  
- 0 indicates random prediction  
- −1 indicates total disagreement

---

### Cohen's Kappa

Cohen's Kappa measures the agreement between prediction and ground truth while accounting for agreement occurring by chance.  
Find more information about [Cohen's Kappa](https://metrics-reloaded.dkfz.de/metric-library/cohens_kappa).

$$ \text{WCK} = \frac{p_0^w - p_e^w}{1 - p_e^w},$$

$$
p_0^w
=
\frac{
w_{\mathrm{TP}}\mathrm{TP}
+
w_{\mathrm{TN}}\mathrm{TN}
+
w_{\mathrm{FP}}\mathrm{FP}
+
w_{\mathrm{FN}}\mathrm{FN}
}{
\mathrm{TP} + \mathrm{TN} + \mathrm{FP} + \mathrm{FN}
}
$$

$$
p_e^w =
w_{\mathrm{TP}}
\cdot
\frac{(\mathrm{TP}+\mathrm{FP})(\mathrm{TP}+\mathrm{FN})}{\mathrm{TP}+\mathrm{TN}+\mathrm{FP}+\mathrm{FN}}
+
w_{\mathrm{TN}}
\cdot
\frac{(\mathrm{TN}+\mathrm{FP})(\mathrm{TN}+\mathrm{FN})}{\mathrm{TP}+\mathrm{TN}+\mathrm{FP}+\mathrm{FN}}
+
w_{\mathrm{FN}}
\cdot
\frac{(\mathrm{FN}+\mathrm{FP})(\mathrm{FN}+\mathrm{TN})}{\mathrm{TP}+\mathrm{TN}+\mathrm{FP}+\mathrm{FN}}
+
w_{\mathrm{FP}}
\cdot
\frac{(\mathrm{FP}+\mathrm{TP})(\mathrm{FP}+\mathrm{TN})}{\mathrm{TP}+\mathrm{TN}+\mathrm{FP}+\mathrm{FN}}
$$


**Interpretation:**  
Values range from −1 to 1.

- 1 indicates perfect agreement  
- 0 indicates agreement equivalent to chance  
- negative values indicate worse than chance


---

### Positive Likelihood Ratio (LR+)

LR+ indicates the factor by which a positive prediction occurs more frequently among actual positive samples than among 
actual negative samples. 
Find more information about [LR+](https://metrics-reloaded.dkfz.de/metric-library/positive_likelihood_ratio).

$$
\text{LR}^+ = \frac{\text{Sensitivity}}{1 - \text{Specificity}}
$$

**Interpretation:**  
Values range from 0 to ∞. Higher values indicate stronger evidence.

---

### Net Benefit (NB)

NB validates the quality of a model intended to support a specific clinical decision. NB gives the ‘net’ proportion of 
TPs that results from a prediction. This is equivalent to the proportion of TPs in the absence of FPs. 
For its calculation, NB considers a task-related risk threshold (= exchange rate between the benefit of TPs and harm of 
FPs).
Find more information about [NB](https://metrics-reloaded.dkfz.de/metric-library/net_benefit).


$$
\text{NB} =\;
\frac{\text{TP}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}
-\;
\frac{\text{FP}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}
\cdot \Big( \frac{\text{p}_t}{1 - \text{p}_t} \Big) 
$$

Where:

- $N$ is the number of samples  
- $p_t$ is the decision threshold  

**Interpretation:**  
Values range from -∞ to 1. Higher values indicate better model performance.

---

### Normalised Expected Cost (ECn)

EC is a generalization of the probability of error (which is, in turn, 1 - Accuracy) for cases in which errors cannot 
all be considered to have equally severe consequences. It is defined as the expectation of the cost, where the 
cost incurred on a certain sample depends on the sample's class and the decision made for that sample. In practice,
the expectation can be estimated as a simple average of the costs over the evaluation samples. EC describes 
the weighted sum of error rates. It can be used to measure discrimination and calibration in one score. 

$$
EC = \text{w}_{\text{miss}} \cdot \frac{\text{FN}}{\text{TP} + \text{FN}} \cdot \frac{\text{TP} + \text{FN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}} + \text{w}_{\text{FA}} \cdot \frac{\text{FP}}{\text{TN} + \text{FP}} \cdot (1 - \frac{\text{TP} + \text{FN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}})
$$


**Interpretation:**  
Values range from 0 to ∞. Lower values indicate better model performance.


## Distance-based metrics

### Average Symmetric Surface Distance (ASSD)

ASSD measures the average distance between the surfaces of two segmentations.  
Find more information about [ASSD](https://metrics-reloaded.dkfz.de/metric-library/average_symmetric_surface_distance).

$$
\text{ASSD}(\text{A}, \text{B}) =
\frac{\displaystyle \sum_{\text{a} \in \text{A}} d(\text{a}, \text{B}) \, + \,
        \displaystyle \sum_{\text{b} \in \text{B}} d(\text{b}, \text{A})}
       {|\text{A}| + |\text{B}|}
$$

$$ \text{d}(\text{a}, \text{B}) = \min_{\text{b} \in \text{B}} d(\text{a}, \text{b}) $$



**Interpretation:**  
Values range from 0 to ∞. Lower values indicate better agreement between surfaces.

---

### Mean Average Surface Distance (MASD)

MASD measures the mean of the averages over all shortest distances from all sampled points on one boundary to any other point on another boundary. 
Find more information about [MASD](https://metrics-reloaded.dkfz.de/metric-library/masd).

$$ \text{MASD}(A, B) = \frac{1}{2} \Biggl(
\frac{\displaystyle \sum_{a \in A} d(a, B) \,}{|A|} + \frac{ \,
        \displaystyle \sum_{b \in B} d(b, A)} {|B|} \Biggl) 
$$

$$ d(a,B) = \min_{b \in B} d(a,b) $$

**Interpretation:**  
Values range from 0 to ∞. Lower values indicate better agreement between surfaces.

---

### Hausdorff Distance (HD)

HD is the largest of all the distances from a point on one boundary to the closest point on the other boundary.
Find more information about [HD](https://metrics-reloaded.dkfz.de/metric-library/hd).

$$
\text{HD}(\text{A}, \text{B})
= \max \Bigl\{\max_{\text{a} \in \text{A}} d(\text{a}, \text{B}), \,
\max_{\text{b} \in \text{B}} d(\text{b}, \text{A}) \Bigr\}
$$

$$ d(\text{a}, \text{B}) = \min_{\text{b} \in \text{B}} d(\text{a}, \text{b}) $$

**Interpretation:**  
Values range from 0 to ∞. Lower values indicate better agreement between surfaces.


---

### Percentile Hausdorff Distance (xᵗʰ HD)

The xᵗʰ percentile of the Hausdorff Distance (HD) measures the xᵗʰ percentile of all the distances from a point on one boundary to the closest point on the other boundary. A common value is x = 95 (HD95). 
Find more information about [xᵗʰ HD](https://metrics-reloaded.dkfz.de/metric-library/xhd).

$$
\text{HD95}(\text{A}, \text{B})
= \max \Bigl\{ d_{95}(\text{A}, \text{B}), \,
d_{95}(\text{B}, \text{A}) \Bigr\}
$$

$$ d_{95}(\text{A}, \text{B}) = \text{x}_{\! \substack{95 \\ \text{a} \in \text{A}}} \Bigl\{ \min_{\text{b} \in \text{B}} d(\text{a}, \text{b})\Bigr\} $$

**Interpretation:**  
Values range from 0 to ∞. Lower values indicate better agreement between surfaces.

---

### Normalized Surface Distance (NSD)

NSD measures the DSC on boundary pixels with an uncertainty margin. The degree of strictness for what constitutes a 
correct boundary is represented by the tolerance parameter τ. Only boundary parts within the border regions defined by 
τ are counted as TP. NSD therefore captures known uncertainties in the reference and allows acceptable deviations from 
the reference for the predicted boundary. 
Find more information about [NSD](https://metrics-reloaded.dkfz.de/metric-library/normalized_surface_distance).

$$
\text{NSD}(\text{A}, \text{B})^{(\tau)} =
\frac{
\lvert S_\text{A} \cap {\mathcal{B}_\text{B}}^{(\tau)} \rvert + \lvert S_\text{B} \cap {\mathcal{B}_\text{A}}^{(\tau)} \rvert
}{
\lvert S_{\text{A}} \rvert + \lvert S_{\text{B}} \rvert
}
$$

Where:

- $\tau$ is a distance tolerance

**Interpretation:**  
Values range from 0 to 1. Higher values indicate better surface agreement.

---

### Boundary IoU

Boundary IoU measures the overlap between the predicted and reference boundaries up to a predefined width d. 
Find more information about [Boundary IoU](https://metrics-reloaded.dkfz.de/metric-library/boundary_intersection_over_union).

$$
\text{Boundary IoU}(\text{A}, \text{B}) = \frac{|\text{A}_{\text{d}} \cap \text{B}_{\text{d}}|}{|\text{A}_{\text{d}}| + |\text{B}_{\text{d}}| - |\text{A}_{\text{d}} \cap \text{B}_{\text{d}}|} = \frac{|\text{A}_{\text{d}} \cap \text{B}_{\text{d}}|}{|\text{A}_{\text{d}} \cup \text{B}_{\text{d}}|}
$$


**Interpretation:**  
Values range from 0 to 1. Higher values indicate better surface agreement.
