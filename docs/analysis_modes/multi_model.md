# Multi-model performance comparison

The **Multi-model performance comparison** analysis mode in AUDIT allows users to evaluate and compare a set of
segmentation models on a single dataset, across multiple metrics and tumor regions.

It provides both a summary table and an interactive boxplot-based visualization, where each box represents the 
performance distribution of a model on a specific region and metric. This allows users to intuitively assess which 
models perform better in which contexts, identify strengths and weaknesses, and support informed model selection decisions.

---

The purpose of multi-model performance analysis is to:

- **Compare several segmentation models** on the same dataset under identical conditions.
- **Assess performance across multiple tumor regions and evaluation metrics.**
- **Identify strengths and weaknesses** of each model depending on the region or metric.
- **Visualize inter-model differences** in terms of robustness, variability, and outlier behavior.
- **Support model benchmarking**, ensemble design, and model selection over different model versions.

---

## 🎥 Demo video


Below is a short video that walks you through the segmentation error matrix mode interface:

[![Watch the video](https://img.youtube.com/vi/usqE4YibdfA/0.jpg)](https://youtu.be/usqE4YibdfA)

---


## ⚙️ User Configuration

### 1. **Dataset selection**

In this mode, users can select only one dataset. This ensures a consistent and fair comparison, as all models are 
evaluated on the exact same subjects.

In this mode, users can select a single dataset from the dropdown in the sidebar. Unlike other modes in AUDIT (such as 
the Multivariate analysis mode), the multi-model performance analysis is not designed for multi-dataset comparison within the 
same view. Instead, its purpose is to provide a focused and detailed evaluation of how a segmentation model performs on 
a specific dataset, ensuring a consistent and fair comparison, as all models are evaluated on the exact same subjects.

It is important that the segmentation labels and the ground truth labels must be aligned properly; otherwise, the 
analysis mode will not work correctly. You can follow this [tutorial](../tutorials/postprocessing_segmentations.md) where it is explained how to modify the 
dataset labels to ensure proper alignment.


!!! warning
    Ensure that all selected models were evaluated using the same dataset version, and that predictions  
    were computed using consistent preprocessing and alignment protocols.  
    Otherwise, performance comparisons may be biased.

---

### 2. **Model selection**

Users can select two or more segmentation models to include in the comparison. These models must have available 
prediction files and precomputed evaluation metrics for the selected dataset by AUDIT's backend. Once selected, the 
dashboard will automatically load and visualize their performance across the chosen metrics and regions.

Each model is represented by a distinct color in the boxplot grid, ensuring easy visual differentiation and making it 
straightforward to spot performance differences across metrics and tumor subregions.

This mode is especially useful when:
    
- **Comparing successive versions** of the same model (e.g., v1, v2, v3) where each version incorporates incremental improvements such as new loss functions, or preprocessing pipelines.
- **Conducting ablation studies**, where specific components (e.g., attention modules, auxiliary branches, normalization layers) are removed to evaluate their contribution to overall performance.
- **Evaluating model robustness across regions** to determine whether improvements are consistent or limited to certain tumor substructures.
- **Benchmarking against baseline** methods such as classical segmentation tools or previously published models.

!!! tip
    This mode is ideal for researchers and developers who want to track progress over time,
    validate architectural changes, or prepare comparative figures for scientific publications.
    Including both baseline and experimental models can help identify trade-offs and guide future improvements.

---


### 3. **Region selection**

By default, model performance is shown aggregated by region. This means that both the summary table and each boxplot 
represent a model’s average performance across all tumor subregions. This aggregated view is useful to quickly grasp 
overall trends and identify which models perform best on average.

However, AUDIT also allows users to disaggregate performance by individual regions, offering a more detailed and 
fine-grained analysis. When this option is enabled, the boxplots are split by region, and the performance of each model 
is shown separately for each tumor subregion.

This disaggregated view is particularly important in tumor segmentation tasks, where subregions may differ 
significantly in size, intensity, morphology, or clinical relevance. A model may achieve a high average Dice score by 
performing well on large, easy-to-segment regions, while still struggling with smaller or more heterogeneous areas, 
a pattern that would only become visible when analyzing regions individually.

!!! tip
    Use the disaggregated view to detect region-specific weaknesses, such as models that consistently underperform on 
    small enhancing tumor regions or show high boundary error in the tumor core.

---

### 4. **Metric selection**

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

## 📊 Visualization

The **Multi-model performance comparison** mode provides two complementary dashboards:

---

### Dashboard 1: Summary table

At the top of the interface, a **summary table** displays the **mean ± standard deviation** of each selected metric for 
all selected models. These values are computed across all subjects, and by default, aggregated over all tumor regions.

This compact overview enables users to quickly identify which models perform best on average, and which ones exhibit 
higher variability.

> ![Summary table — aggregated view](../assets/dashboards_examples/multi_model_performance/summary_table_agg_l.png#only-light)
> ![Summary table — aggregated view](../assets/dashboards_examples/multi_model_performance/summary_table_agg_d.png#only-dark)
> *Figure 1:* Summary table showing model performance aggregated over all tumor regions.

The "Aggregated" checkbox above the table allows switching between showing average scores across all 
regions or displaying each region individually.

> ![Summary table — disaggregated view](../assets/dashboards_examples/multi_model_performance/summary_table_disagg_l.png#only-light)
> ![Summary table — disaggregated view](../assets/dashboards_examples/multi_model_performance/summary_table_disagg_d.png#only-dark)
> *Figure 2:* Summary table with the "Aggregated" option disabled. Each region is shown separately for more granular analysis.

---

### Dashboard 2: Boxplot visualization

Additionally to the table, an **interactive boxplot** provides a detailed view of the distribution of metric values. This
plot visualizes the variability, median, and outliers for each selected metric, grouped by model.

By default, the plot shows **aggregated values** — i.e., one box per model and metric, summarizing performance across 
all tumor regions.

- **X-axis**: Selected metrics (e.g., Dice, Jaccard, Sensitivity)  
- **Y-axis**: Metric value  
- **Color**: Each model is assigned a distinct color  
- **Boxes**: One per model and metric, showing median, quartiles, and outliers

> ![Boxplots comparing model performance (aggregated)](../assets/dashboards_examples/multi_model_performance/multimodel_performance_l.svg#only-light)
> ![Boxplots comparing model performance (aggregated)](../assets/dashboards_examples/multi_model_performance/multimodel_performance_d.svg#only-dark)
> *Figure 3:* Boxplots showing the distribution of aggregated model performance across metrics. Each color represents a different model.

---

All plots are interactive, powered by _Plotly_, allowing users to:

- Toggle datasets on and off
- Zoom and pan within plots
- Export high-resolution images
- Hover to inspect exact values

Whether you're debugging unexpected results or preparing figures for publication, this analysis mode is a core part of 
the AUDIT toolkit.
