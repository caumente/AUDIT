# Single model performance

The **Single model performance** analysis mode in AUDIT allows users to evaluate how a given segmentation model performs
across multiple datasets based on a chosen feature and evaluation metric.

It provides a **univariate scatter plot** where each point represents a subject, placed according to:
- **X-axis:** A selected feature (e.g., maximum intensity in T1, tumor volume, etc.)
- **Y-axis:** A performance metric (e.g., Dice, Hausdorff distance, etc.)

This enables intuitive exploration of how specific image characteristics relate to model performance, helping identify 
trends, outliers, or systematic failures.

---

The purpose of single model performance analysis is to:

- **Assess model performance** in relation to a single image-derived feature.
- **Compare how the same model behaves** across multiple datasets or cohorts.
- **Identify systematic failure patterns** linked to specific feature ranges (e.g., intensity, volume).
- **Detect outlier cases** where the model performs unexpectedly well or poorly.
- **Understand how specific features relate to performance**, to guide model improvement and debugging.

---

## 🎥 Demo video


Below is a short video that walks you through the segmentation error matrix mode interface:

[![Watch the video](https://img.youtube.com/vi/usqE4YibdfA/0.jpg)](https://youtu.be/usqE4YibdfA)

---

## ⚙️ User Configuration

### 1. **Dataset selection**

Users can load and compare multiple datasets simultaneously in the Single model performance analysis mode. This 
enables side-by-side inspection of how models perform across different cohorts — for example, 
across different institutions, scanner protocols, or study years.

Each dataset is automatically assigned a distinct color in all plots, ensuring an easy interpretation.

Datasets can be:

- Selected or deselected using the dedicated selector panel on the left-hand side of the dashboard.
- Toggled directly from the interactive Plotly legend, which allows temporary hiding/showing of datasets with a single click.

While the Plotly legend interaction is useful for quick comparisons, we recommend using the left-side dataset selector 
for a more stable and consistent user experience, especially when exporting plots or applying filters.

!!! warning
    To ensure meaningful comparisons, all datasets should ideally be registered to the same reference space  
    and preprocessed in a consistent way. Otherwise, differences in voxel spacing, intensity scaling, or orientation  
    may introduce bias in both features and performance metrics.

---

### 2. **Model selection**

Users must choose one of the available segmentation models to evaluate in this mode. This model must have associated 
prediction files, from which performance metrics were precomputed by the AUDIT backend. These precalculated 
metrics are then loaded and visualized in the scatter plot.

The selected model determines which performance values are shown on the **Y-axis**, one point per subject. This allows 
users to inspect how the model performs across subjects, in relation to a selected feature on the **X-axis**.

!!! tip
    If you have multiple models available for the same dataset, switching between them is a powerful way to 
    compare their behavior under the same data conditions and identify strengths or weaknesses specific to each 
    architecture.

---

### 3. **Metric selection**

Users must select a single evaluation metric that quantifies the segmentation quality of the chosen model. As mentioned, 
these metrics are precomputed by the AUDIT backend and loaded from disk when the analysis is launched. The selected 
metric is plotted on the **Y-axis**, allowing users to analyze performance relative to the selected feature (X-axis).

AUDIT natively supports the following metrics:

| Metric           | Description                                                                                       | Interpretation              |
|:------------------|:--------------------------------------------------------------------------------------------------|:-----------------------------|
| `dice`           | Dice coefficient; measures the overlap between predicted and ground truth masks.                  | Higher is better            |
| `jacc`           | Jaccard Index (Intersection over Union); similar to Dice but penalizes false positives more.      | Higher is better            |
| `accu`           | Accuracy; proportion of correctly classified voxels across all classes.                           | Higher is better            |
| `prec`           | Precision; proportion of predicted positives that are true positives (i.e., few false positives). | Higher is better            |
| `sens`           | Sensitivity (Recall); proportion of true positives detected (i.e., few false negatives).          | Higher is better            |
| `spec`           | Specificity; proportion of true negatives correctly identified.                                   | Higher is better            |
| `haus`           | Hausdorff distance (95% percentile); measures the worst-case boundary error.                      | Lower is better             |
| `lesion_size`    | Total volume of the predicted lesion, in mm³.                                                     | Application-dependent       |

Each metric offers insight into different aspects of model performance:

- **Overlap metrics** like Dice and Jaccard assess spatial agreement.
- **Threshold metrics** like precision and sensitivity are useful for imbalance analysis.
- **Distance metrics** (e.g., Hausdorff) reflect boundary accuracy.
- **Lesion size** serves as a complementary indicator to understand under- or over-segmentation.

!!! warning
    Some metrics (especially `dice`, `haus`, or `lesion_size`) may behave differently across regions with different sizes.  
    Small structures are more sensitive to minor errors, so always interpret values in context.

---

### 4. **Feature selection**

Users must choose a feature to use for the **X-axis**. Features are extracted from the images and segmentations and 
can belong to various categories:

| Feature      | Description                                                                  | Example                                 |
|:-------------|:-----------------------------------------------------------------------------|:----------------------------------------|
| Statistical  | Descriptive measures derived from intensity distributions.                   | Mean, standard deviation, maximum       |
| Texture      | Quantitative descriptors of local intensity patterns (GLCM-based).           | Entropy, contrast, homogeneity          |
| Spatial      | Anatomical or geometric positioning of segmented regions.                    | Center of mass (x, y, z)                |
| Tumor        | Morphological properties extracted from segmentation masks.                  | Lesion volume, tumor location           |

Some features depend heavily on the imaging modality, and comparisons between datasets are only meaningful when 
extracted from preprocessed MRIs. Texture features in particular are highly sensitive to variations in acquisition 
protocols and preprocessing pipelines. This sensitivity arises because descriptors like entropy, contrast, and energy 
are affected by voxel size and image spacing, intensity range and quantization strategy, and other technical aspects 
related to the scanners. Such technical differences are especially relevant in multi-center studies, where spatial 
resolution and image quality may vary substantially.

Other features, such as tumor volume, center of mass, or spatial location, are typically derived from segmentation 
masks that take into account the voxel spacing, and are independent of intensity information. These are more robust 
to differences in acquisition and preprocessing, making them suitable for comparisons even across heterogeneous cohorts.

!!! info
    _More technical details can be found in_ [our publication](https://arxiv.org/) _and within the_ [API reference](https://caumente.github.io/AUDIT/API_reference/features/feature_extraction/).

---

## 📊 Visualization

The **single model performance** dashboard displays an interactive 2D scatter plot in which each
point represent a subject. Each dot corresponds to a subject, positioned by its feature value (X-axis) and performance 
metric (Y-axis), and colored by dataset.


> ![2D scatter plot of single model performance across datasets](../assets/dashboards_examples/single_model_performance/single_model_performance_l.svg#only-light)
> ![2D scatter plot of single model performance across datasets](../assets/dashboards_examples/single_model_performance/single_model_performance_d.svg#only-dark)
> *Figure 1:* A scatter plot showing the relationship between a selected features and metric across datasets. Each point represents a subject and is colored by dataset.


!!! info
    The “Aggregated” checkbox allows toggling between:
    - **Aggregated mode:** Each point summarizes the subject across all regions.
    - **Disaggregated mode:** The plot is faceted by region, showing one subplot per tumor region.


---

## 🧰 Additional options

### Highlighting points

Users can **double-click on a point** to highlight a specific subject in red.  
Highlighted points are preserved across views and can be reset by clicking the **Reset highlighted cases** button.

This is useful for inspecting specific subjects with particularly low or high performance. Understanding why some cases 
are easier (or harder) to segment can be crucial to improving model generalization capabilities.

> ![2D scatter plot of single model performance highlighted across datasets](../assets/dashboards_examples/single_model_performance/single_model_performance_highlighted_l.svg#only-light)
> ![2D scatter plot of single model performance highlighted across datasets](../assets/dashboards_examples/single_model_performance/single_model_performance_highlighted_d.svg#only-dark)
> *Figure 2:* A scatter plot showing the relationship between a selected features and metric across datasets. Each point represents a subject and is colored by dataset. Notice how there are two specific subjects highlighted in red to monitor their performance.


---

### Aggregating

Users can switch between visualizing the subjects in an aggregated or disaggregated view.  
This is particularly useful to understand which subregions are more challenging to segment.

Additionally, it helps understand how different tumor regions contribute to the overall 
performance distribution. For example, a model might appear robust in aggregated view but show poor performance on 
specific subregions when disaggregated.

In **aggregated view**, performance metrics are computed across the entire segmentation mask (all regions combined).  
In **disaggregated view**, the plot is faceted by region, and each subplot shows region-specific performance.

!!! tip
    Use the **highlighting** option to mark the patients you are interested in,  
    and then switch to the **disaggregated** view. This will show how your selected cases perform across different tumor
    subregions, helping reveal region-specific issues or inconsistencies.

> ![2D disaggregated scatter plot of single model performance highlighted across datasets](../assets/dashboards_examples/single_model_performance/single_model_performance_highlighted_disagg_l.svg#only-light)
> ![2D disaggregated scatter plot of single model performance highlighted across datasets](../assets/dashboards_examples/single_model_performance/single_model_performance_highlighted_disagg_d.svg#only-dark)
> *Figure 3:* A disaggregated view scatter plot showing the relationship between a selected features and metric across datasets. Each point represents a subject and is colored by dataset. Notice how there are two specific subjects highlighted in red to monitor their performance.



---

All plots are interactive, powered by _Plotly_, allowing users to:

- Toggle datasets on and off
- Zoom and pan within plots
- Export high-resolution images
- Hover to inspect exact values

Whether you're debugging unexpected results or preparing figures for publication, this analysis mode is a core part of 
the AUDIT toolkit.
