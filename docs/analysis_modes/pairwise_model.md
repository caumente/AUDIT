# Pairwise model performance comparison

The **Pairwise model performance comparison** analysis mode in AUDIT enables users to directly compare two segmentation 
models by quantifying the improvement in performance between them. This mode provides intuitive visualizations that 
highlight where one model outperforms another, helping researchers understand relative model strengths, identify 
systematic differences, and make evidence-based decisions about model selection and deployment.

It provides a set of **region-based barplot plots** where each one represents a subject, placed according to:

- **X-axis:** A difference in performance between models (e.g., relative Dice, absolute Hausdorff distance, etc.)
- **Y-axis:** Regions of interest (e.g. necrotic, edema, etc.)

---

The purpose of pairwise model performance comparison is to:

- **Compare two segmentation models** head-to-head on the same dataset.
- **Quantify performance differences** using multiple comparison metrics (absolute, relative, ratio).
- **Identify which regions** show the greatest improvement between models.
- **Visualize subject-level variability** in model performance differences.
- **Support statistical validation** of performance differences through hypothesis testing.
- **Guide model selection** by revealing systematic strengths and weaknesses.

---

## 🎥 Demo video

Below is a short video that walks you through the pairwise model performance comparison mode interface:

[![Watch the video](https://img.youtube.com/vi/PLACEHOLDER_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=PLACEHOLDER_VIDEO_ID)

---

## ⚙️ User configuration

### 1. **Dataset selection**

In this mode, users can select only one dataset. This ensures a consistent and fair comparison, as all models are 
evaluated on the exact same subjects.

In this mode, users can select a single dataset from the dropdown in the sidebar. Unlike other modes in AUDIT (such as 
the Multivariate analysis mode), the pair-wise model performance analysis is not designed for multi-dataset comparison within the 
same view. Instead, its purpose is to provide a focused and detailed evaluation of how two segmentation models perform on 
a specific dataset, ensuring a consistent and fair comparison, as all models are evaluated on the exact same subjects.

It is important that the segmentation labels and the ground truth labels must be aligned properly; otherwise, the 
analysis mode will not work correctly. You can follow this [tutorial](../tutorials/Lumiere_postprocessing.md) where it 
is explained how to modify the dataset labels to ensure proper alignment.


!!! warning
    Ensure that all selected models were evaluated using the same dataset version, and that predictions  
    were computed using consistent preprocessing and alignment protocols.  
    Otherwise, performance comparisons may be biased.

---

### 2. **Model selection**

Users must select two models for comparison:

- **Baseline model**: The reference model against which improvements are measured
- **Benchmark model**: The comparison model being evaluated for improvement

The choice of which model serves as baseline versus benchmark affects the interpretation of results:

- **Positive values** indicate the benchmark model performs better than the baseline. 
- **Negative values** indicate the baseline model performs better than the benchmark

Green bars indicate improvement (benchmark > baseline), orange bars indicate decline (benchmark < baseline)

!!! tip
    When comparing an established model against a new architecture, typically the established model serves as the 
    baseline and the new model as the benchmark. This framing makes positive improvements easy to identify.

---

### 3. **Metric selection**

Users must select a single evaluation metric that quantifies the segmentation quality of the chosen model. As mentioned, 
these metrics are precomputed by the AUDIT backend and loaded from disk when the analysis is launched. The selected 
metric is plotted on the **X-axis**.

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

### 4. **Type of comparison**

AUDIT provides three different ways to quantify the improvement between models, each offering different perspectives on performance differences:

#### 1. **Absolute improvement**

$$\text{Absolute} = M_{\text{benchmark}} - M_{\text{baseline}}$$

Measures the raw difference in metric values. For example, if the baseline Dice is 0.75 and the benchmark is 0.80, 
the absolute improvement is +0.05.

It is best for understanding the magnitude of improvement in the original metric units. Simple and intuitive since it directly 
shows how much the metric changed.

#### 2. **Relative improvement**

$$\text{Relative} = \frac{M_{\text{benchmark}} - M_{\text{baseline}}}{M_{\text{baseline}}} \times 100$$

Measures improvement as a percentage of the baseline performance. For example, if the baseline Dice is 0.75 and the 
benchmark is 0.80, the relative improvement is +6.67%.

It is best for comparing improvements across different baseline performance levels. Accounts for the difficulty of 
improvement (harder to improve from 0.90 than from 0.50).

#### 3. **Ratio**

$$\text{Ratio} = \frac{M_{\text{benchmark}}}{M_{\text{baseline}}}$$

Measures the ratio of benchmark to baseline performance. Values greater than 1 indicate improvement.

It is best for understanding multiplicative relationships between model performances. A ratio of 1.10 means the 
benchmark is 10% better than the baseline

!!! tip
    **Relative improvement** is often most informative for comparing models across different datasets or regions, as it accounts for varying difficulty levels. Use **absolute improvement** when you need to report changes in clinically meaningful units.

---

### 5. **Aggregation mode**

Users can toggle between two views using the **Aggregated** checkbox:

#### 1. **Disaggregated view**

Shows performance differences for each subject individually, with bars representing different anatomical regions. This 
subject-level view reveals which subjects benefit most from the benchmark model,whether improvements are consistent 
across subjects, and help discovering subject-specific patterns that may be hidden in averages

#### 2. **Aggregated view**

Shows average performance differences across all subjects, summarized by anatomical region. This cohort-level view 
reveals hich regions show the greatest overall improvement, whether improvements are statistically significant, and
the general trend across the entire dataset

!!! info
    The disaggregated view is particularly useful for identifying outlier subjects or understanding variability, while 
    the aggregated view provides a clearer picture of overall model performance.

---

## 📊 Visualizations

### 1. Subject-level comparison (disaggregated view)

In the disaggregated view, each subject is displayed with a horizontal bar chart showing performance differences across 
anatomical regions.

> ![Subject-level comparison showing performance differences across anatomical regions for individual subjects](../assets/dashboards_examples/pairwise_model_performance/agg_pairwise_model_performance_disagg_l.png#only-light)
> ![Subject-level comparison showing performance differences across anatomical regions for individual subjects](../assets/dashboards_examples/pairwise_model_performance/agg_pairwise_model_performance_disagg_d.png#only-dark)
> *Figure 1:* Subject-level comparison showing performance differences across anatomical regions for individual subjects. Green bars indicate improvement by the benchmark model, while orange bars indicate decline.

Each bar chart includes:

- **Subject ID** and key metadata (lesion location, lesion size)
- **Average baseline and benchmark performance** for context
- **Color coding**: Green bars indicate improvement (benchmark > baseline), orange bars indicate decline (benchmark < baseline)
- **Multiple regions** per subject, enabling region-specific analysis


Sorting options: Users can sort subjects in ascending or descending order by:

- Performance of baseline model
- Performance of benchmark model
- Subject ID

Maximum subjects: Users can limit the number of subjects displayed to focus on the most relevant cases 
(e.g., top 10 subjects with greatest improvement).

Clipping: Users can clip extreme values to focus on the typical range of improvements, preventing outliers from 
dominating the visualization.

!!! tip
    Sort by improvement magnitude in descending order to quickly identify subjects where the benchmark model provides 
    the greatest benefit. This can guide case-specific analysis or help identify what characteristics make certain 
    subjects easier or harder for each model.

---

### Cohort-level comparison (aggregated view)

In the aggregated view, performance differences are averaged across all subjects and displayed as a single bar chart 
with one bar per anatomical region.

> ![Subject-level comparison showing performance differences across anatomical regions for individual subjects](../assets/dashboards_examples/pairwise_model_performance/agg_pairwise_model_performance_l.svg#only-light)
> ![Subject-level comparison showing performance differences across anatomical regions for individual subjects](../assets/dashboards_examples/pairwise_model_performance/agg_pairwise_model_performance_d.svg#only-dark)
> *Figure 2:* Aggregated comparison showing average performance differences across anatomical regions for the entire cohort. Each bar represents the mean improvement or decline for that region.

The aggregated bar chart shows:
- **Average improvement** for each anatomical region
- **Color coding**: Green bars indicate overall improvement, orange bars indicate overall decline
- **Region-level insights**: Which tumor subregions benefit most from the benchmark model

Download option: The aggregated plot can be downloaded as a high-resolution image for reports or publications.

Statistical testing: Users can enable statistical hypothesis testing to determine whether observed differences are 
statistically significant.

!!! warning
    Aggregated results can hide important subject-level variability. Always inspect the disaggregated view to ensure 
    that apparent improvements are consistent across subjects and not driven by a small subset of cases.

---

## 🧪 Statistical testing

AUDIT provides built-in statistical hypothesis testing to validate whether observed performance differences between 
models are statistically significant or could have occurred by chance.

When in **aggregated view**, users can check the "Perform statistical test" option. This triggers an automated analysis 
pipeline that:

1. **Tests parametric assumptions**: Normality and homoscedasticity. Independence is assumed.
2. **Selects appropriate test**: Paired t-test or Wilcoxon signed-rank test
3. **Reports results**: p-value and interpretation

---

#### 1. Parametric assumptions
Before performing the comparison test, AUDIT automatically checks whether the data meet the assumptions required for 
parametric testing:

**Normality test**: Tests whether the performance distributions for both models follow a normal distribution using the Shapiro-Wilk or
Lilliefors test.

- Null hypothesis: The data are normally distributed
- Result: Displays p-value and whether normality assumption is met

For each model, AUDIT displays the normality test results in a table and a histogram showing the distribution of performance values
 
> ![Normality test](../assets/dashboards_examples/pairwise_model_performance/normality_test_and_table_l.png#only-light)
> ![Normality test](../assets/dashboards_examples/pairwise_model_performance/normality_test_and_table_d.png#only-dark)
> *Figure 3:* Normality test performed for baseline and benchmark models. 


**Homoscedasticity test**: Tests whether the two models have equal variances using Levene's test.

- Null hypothesis: The variances are equal
- Result: Displays whether homoscedasticity assumption is met


---

#### 2. Hypothesis testing

Based on the results of the parametric assumptions tests, AUDIT automatically selects the appropriate statistical test:

**Paired Student's t-test** (Parametric): Used when both samples are normally distributed and have equal variances. It 
is appropriate for data meeting the parametric assumptions. 

**Wilcoxon signed-rank test** (Non-parametric): Used when the data violate normality or homoscedasticity assumptions. 

---

#### 3. Report results

The statistical test produces:

- **p-value**: The probability of observing the data if there were truly no difference between models
- **Interpretation**: A plain-language summary of the result

> ![Significance test](../assets/dashboards_examples/pairwise_model_performance/statistical_test_l.png#only-light)
> ![Significance test](../assets/dashboards_examples/pairwise_model_performance/statistical_test_d.png#only-dark)
> *Figure 4:* Statistical significance test performed on baseline and benchmark models. 


!!! warning
    By default, AUDIT uses a significance threshold of α = 0.05. P-values below this threshold indicate statistically 
    significant differences. Users can download the complete dataset used for statistical testing, so we encourage them
    to perform their own analysis.

---

All plots are interactive, powered by _Plotly_, allowing users to:
- Toggle regions on and off
- Zoom and pan within plots
- Export high-resolution images
- Hover to inspect exact values

Whether you're validating a new model architecture, debugging unexpected results, or preparing results for publication, 
the pairwise model performance comparison mode provides the statistical rigor and visual clarity needed to make 
evidence-based decisions about model performance.