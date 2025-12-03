# Subject exploration

The **Subject exploration** analysis mode in AUDIT provides a detailed view of individual subjects, allowing users to inspect 
their feature profiles and determine whether they represent outliers within their cohort. This mode supports targeted 
investigation of specific cases, helping researchers understand subject-level variability and identify atypical 
patterns that may warrant further investigation or quality control.

---

The purpose of subject exploration is to:

- **Inspect individual subject characteristics** across all extracted features.
- **Identify outlier subjects** using statistical detection methods.
- **Compare subject values** against cohort statistics (median, mean, standard deviation).
- **Support quality control** by flagging subjects with unusual feature profiles.
- **Enable targeted case review** for subjects with unexpected model performance or clinical presentation.

---

## 🎥 Demo video

Below is a short video that walks you through the subject exploration mode interface:

[![Watch the video](https://img.youtube.com/vi/PLACEHOLDER_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=PLACEHOLDER_VIDEO_ID)

---

## ⚙️ User Configuration

### 1. **Dataset selection**

Users must first select a single dataset from which to explore individual subjects. Unlike other analysis modes that 
support multi-dataset comparison, subject exploration focuses on understanding individuals within a specific 
cohort context.

The selected dataset determines:
- Which subjects are available for inspection
- The reference population used for outlier detection
- The statistical benchmarks (median, mean, standard deviation) displayed for comparison

!!! warning
    To ensure meaningful comparisons, all datasets should ideally be registered to the same reference space  
    and preprocessed in a consistent way. Otherwise, differences in voxel spacing, intensity scaling, or orientation  
    may introduce bias in both features and performance metrics.

---

### 2. **Subject selection**

After selecting a dataset, users choose a specific subject ID to inspect. The interface displays all subjects 
available within the selected dataset, and users can select one from a dropdown menu.

Once selected, the dashboard displays a complete feature profile for that subject across all feature categories, 
including statistical comparison against the rest of the cohort and an outlier status for each feature (determined 
using the IQR method).

This mode is particularly useful when:
- Investigating subjects flagged in other analysis modes (e.g., poor model performance)
- Performing quality control on newly acquired data
- Understanding why certain subjects behave differently than expected

---

## 📊 Visualizations

### Subject information

This section provides a comprehensive overview of the selected subject's feature values, organized by feature category for clarity.

Features are displayed in separate tables, one for each category:

| Feature Category | Description | Example Features |
|:-------------|:-----------------------------------------------------------------------------|:----------------------------------------|
| Statistical | Descriptive measures derived from intensity distributions. | Mean, standard deviation, maximum |
| Texture | Quantitative descriptors of local intensity patterns (GLCM-based). | Entropy, contrast, homogeneity |
| Spatial | Anatomical or geometric positioning of segmented regions. | Center of mass (x, y, z) |
| Tumor | Morphological properties extracted from segmentation masks. | Lesion volume, tumor location |

Each table shows:

- **Feature name**: The specific feature being measured
- **Value**: The subject's value for that feature

This organization makes it easy to quickly scan for unusual values or patterns within specific feature domains.

!!! info
    More technical details about feature extraction can be found in [our publication](https://doi.org/10.1016/j.cmpb.2025.108991) 
    and within the [API reference](https://caumente.github.io/AUDIT/API_reference/features/feature_extraction/).

---

### IQR outlier detection

The IQR (Interquartile Range) outlier detection section automatically identifies whether the selected subject exhibits 
outlier values for any extracted feature, relative to the rest of the cohort.

#### 1. Detection method

The IQR method defines outliers based on the spread of the middle 50% of the data:

1. Calculate Q1 (25th percentile) and Q3 (75th percentile) for each feature across the cohort
2. Compute IQR = Q3 - Q1
3. Define outlier bounds:
   - Lower bound = Q1 - (deviation × IQR)
   - Upper bound = Q3 + (deviation × IQR)
4. Flag the subject if its value falls outside these bounds

By default, the deviation multiplier is set to **1.5** (standard outliers). Users can enable extreme outlier detection
by checking the "Extreme outlier" option, which uses a deviation multiplier of **3.0**.

[//]: # (!!! warning)

[//]: # (    The outlier detection algorithm requires all metadata columns to be numeric. If non-numeric columns are present, )

[//]: # (    the analysis will fail with an error message prompting you to clean your metadata.)

#### 2. Interpretation

The outlier table displays only features for which the subject is flagged as an outlier. For each flagged feature, the table shows:

| Column | Description |
|:-------|:------------|
| **Feature** | Name of the feature |
| **Median (Dataset)** | Median value across the cohort |
| **Mean ± Std (Dataset)** | Mean and standard deviation across the cohort |
| **Subject** | The subject's value for this feature |

If the subject is **not an outlier** for any feature, a message is displayed confirming this.

!!! tip
    Use the extreme outlier setting to focus only on the most severe deviations. Standard outliers (1.5 × IQR) capture moderate deviations, while extreme outliers (3.0 × IQR) highlight only the most unusual cases.

---

All plots are interactive, powered by _Plotly_, allowing users to:

- Toggle datasets on and off
- Zoom and pan within plots
- Export high-resolution images
- Hover to inspect exact values

Whether you're debugging unexpected results or preparing figures for publication, this analysis mode is a core part of 
the AUDIT toolkit.

