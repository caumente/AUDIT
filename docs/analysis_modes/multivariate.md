# Multivariate feature analysis

The **Multivariate analysis mode** in AUDIT enables users to investigate how multiple features interact with each other across different datasets. It provides a two-dimensional scatter plot where each data point represents a subject, and its position is determined by two selected features. This visualization is particularly useful for detecting complex patterns, identifying correlations, and revealing dataset-specific behaviors or outliers that may not be visible in univariate analyses.

---

The goals of multivariate analysis are to:

- **Explore relationships between pairs of features** across multiple datasets.
- **Detect hidden clusters or trends** in the feature space.
- **Identify dataset shifts** or feature interactions that might affect model performance.
- **Spot outliers** that deviate from the main population.
- **Visually compare cohorts** in a shared 2D space.

---

## 🎥 Demo video

Below is a short video that walks you through the multivariate interface:

[![Watch the video](https://img.youtube.com/vi/tkXZVlTHgxE/0.jpg)](https://www.youtube.com/watch?v=tkXZVlTHgxE)

---

## ⚙️ User configuration

### 1. **Dataset Selection**

Users can load and compare multiple datasets simultaneously in the Multivariate analysis mode. This 
enables side-by-side inspection of how a given feature varies across different cohorts — for example, 
across different institutions, scanner protocols, or study years.

Each dataset is automatically assigned a distinct color in all plots, ensuring an easy interpretation.

Datasets can be:

- Selected or deselected using the dedicated selector panel on the left-hand side of the dashboard.
- Toggled directly from the interactive Plotly legend, which allows temporary hiding/showing of datasets with a single click.

While the Plotly legend interaction is useful for quick comparisons, we recommend using the left-side dataset selector 
for a more stable and consistent user experience, especially when exporting plots or applying filters.

### 2. **Feature Selection (X and Y axes)**

Users must select two features, one for the X-axis and one for the Y-axis, from the available categories:

| Feature      | Description                                                                  | Example                                 |
|:-------------|:-----------------------------------------------------------------------------|:----------------------------------------|
| Statistical  | Descriptive measures derived from intensity distributions.                   | Mean, standard deviation, maximum       |
| Texture      | Quantitative descriptors of local intensity patterns (GLCM-based).           | Entropy, contrast, homogeneity          |
| Spatial      | Anatomical or geometric positioning of segmented regions.                    | Center of mass (x, y, z)                |
| Tumor        | Morphological properties extracted from segmentation masks.                  | Lesion volume, tumor location           |

The combination of different types of features (e.g., texture vs. spatial) can help uncover intricate data patterns or technical biases.

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

### 3. **Color Feature**

In addition to selecting the X and Y axes, users can define a third variable to control the color of each data point in 
the scatter plot. This feature enables a richer multivariate exploration by adding a visual encoding of an additional 
dimension, effectively transforming the 2D plot into a pseudo-3D representation.

The available options include:

- **Dataset** (default): Colors each point based on the dataset it belongs to. This is particularly useful when 
    comparing cohorts, such as data from different hospitals, protocols, or population groups. Patterns of separation, 
    overlap, or clustering between datasets can provide insight into dataset shifts or cohort-specific trends.

- **Any other available feature**: Users may also choose to color points based on the value of a specific feature, such 
    as tumor volume, center of mass, texture entropy, or any other scalar variable present in the dataset. This allows 
    researchers to visually explore how a third variable distributes over the 2D feature space and whether it aligns 
    with certain regions, clusters, or gradients.


Colorbars are dynamically generated when using feature-based coloring, providing a reference scale for 
interpretation. Continuous variables use a sequential or diverging colormap, while categorical features are 
represented using distinct colors.

!!! tip
    When coloring by a continuous feature, watch for visual patterns such as localized extremes. These often indicate a 
    non-trivial interaction between the color feature and the selected X/Y pair, which may warrant deeper investigation 
    or stratified modeling approaches.

### 4. **Highlight Subject**

The _Highlight subject_ option allows users to trace the behavior of an individual patient (or subject) across 
plots. By entering a specific subject ID and specifying the corresponding dataset, the selected subject will be 
visually highlighted in the dashboard, where the subject appears as a clearly marked point (e.g., with a 
different color or shape).

This feature is particularly valuable in contexts such as detecting whether a subject is an outlier or aligns with cohort 
expectations or verifying how individuals from different cohorts are distributed in shared feature space.

!!! tip
    When analyzing extreme values, this feature can help determine whether a subject truly deviates from the cohort or 
    lies within natural variability.

---

## 📊 Visualization

The **Multivariate analysis mode** displays an interactive 2D scatter plot:

> ![2D scatter plot of multivariate features across datasets](../assets/dashboards_examples/multivariate/multivariate_analysis_dataset_l.svg#only-light)
> ![2D scatter plot of multivariate features across datasets](../assets/dashboards_examples/multivariate/multivariate_analysis_dataset_d.svg#only-dark)
> *Figure 1:* A scatter plot showing the relationship between two selected features across datasets. Each point represents a subject and is colored by dataset.


> ![3D scatter plot of multivariate features across datasets](../assets/dashboards_examples/multivariate/multivariate_analysis_color_feature_l.svg#only-light)
> ![3D scatter plot of multivariate features across datasets](../assets/dashboards_examples/multivariate/multivariate_analysis_color_feature_d.svg#only-dark)
> *Figure 2:* A scatter plot showing the relationship between three selected features across datasets. X-axis and Y-axis represent Kurtosis and 
   Skewness fo FLAIR sequence intensity pixels. Color represents tumor location for enhancing region.


---

All plots are interactive, powered by _Plotly_, allowing users to:

- Toggle datasets on and off
- Zoom and pan within plots
- Export high-resolution images
- Hover to inspect exact values

Whether you're debugging unexpected results or preparing figures for publication, this analysis mode is a core part of 
the AUDIT toolkit.
