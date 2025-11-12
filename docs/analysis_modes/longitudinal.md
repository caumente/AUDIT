# Longitudinal analysis

The **Longitudinal analysis** mode in AUDIT allows users to track how lesion sizes evolve over time in individual 
subjects. It compares observed (ground truth) and predicted lesion sizes across multiple timepoints, providing insight 
into how well a model captures progression or regression trends.

The goals of longitudinal analysis are to:

- Assess how well a model predicts lesion sizes over time.
- Evaluate temporal consistency in predictions across multiple scans.
- Identify systematic over- or under-estimation of lesion progression.
- Understand patient-specific modeling behavior.
- Support clinical and research decisions involving disease monitoring.

---

## 🎥 Demo video

Below is a short video that walks you through the longitudinal analysis mode interface:

[![Watch the video](https://img.youtube.com/vi/Piyo76knuVY/0.jpg)](https://youtu.be/Piyo76knuVY)

---

## ⚙️ User Configuration

### 1. **Dataset selection**

Users can select a single dataset from the dropdown in the sidebar. Unlike other modes in AUDIT (such as 
the Multivariate analysis mode), the longitudinal analysis is not designed for multi-dataset comparison within the 
same view. Instead, its purpose is to provide a focused and detailed evaluation of how a segmentation model performs on 
a case from a specific dataset.

Make sure that:
- The dataset contains multiple timepoints per subject.
- The label alignment is correct across timepoints (ground truth and predictions must refer to the same anatomical regions).
- The same dataset version and preprocessing pipeline are used for all models being analyzed.

It is important that the segmentation labels and the ground truth labels are aligned properly; otherwise, the 
analysis mode will not work correctly. You can follow this [tutorial](../tutorials/Lumiere_postprocessing.md) where it is explained how to modify the 
dataset labels to ensure proper alignment.

!!! warning
    Ensure that all selected models were evaluated using the same dataset version, and that predictions  
    were computed using consistent preprocessing and alignment protocols.  
    Otherwise, performance comparisons may be biased.

---

### 2. **Model selection**

Users must choose one of the available segmentation models to evaluate in this mode. This model must have associated 
prediction files, from which performance metrics were precomputed by the AUDIT backend. These precalculated 
metrics are then loaded and visualized in the timeline.

AUDIT will automatically:

- Load precomputed lesion sizes (in mm³) from the model's prediction files.
- Compare these with the ground truth lesion sizes.
- Display both trajectories (predicted and observed) along a timeline.

!!! tip
    If you have multiple models available for the same dataset, switching between them is a powerful way to 
    compare their behavior under the same data conditions and identify strengths or weaknesses specific to each 
    architecture.

---

### 3. **Select the subject ID to visualize**

Users have the option to select which subject(s) they want to analyze.

Selecting an individual subject ID will display the longitudinal analysis for that single case. This 
allows detailed inspection of how the model performed on that particular subject, helping to identify 
subject-specific errors or unique segmentation challenges.

This flexibility enables both granular, case-by-case evaluation and broad, cohort-level assessment within the same 
interface.

## 📊 Visualization

The longitudinal analysis panel provides a detailed and interactive visualization of how lesion sizes evolve over time 
for a selected subject. The x-axis represents the different timepoints (e.g., baseline and follow-up scans), while 
the y-axis shows lesion size in cubic millimeters (mm³). This enables users to inspect the temporal dynamics of lesion 
progression or regression, both in the ground truth and in the model predictions.

> ![Longitudinal analysis example](../assets/dashboards_examples/longitudinal/longitudinal_analysis_l.svg#only-light)  
> ![Longitudinal analysis example](../assets/dashboards_examples/longitudinal/longitudinal_analysis_d.svg#only-dark)  
> *Figure 1:* Longitudinal analysis mode in AUDIT. Comparison of observed (orange solid line) and predicted (yellow solid line) lesion sizes across timepoints. Percentage values over the lines indicate tumor growth or shrinkage between consecutive timepoints. Dotted blue lines and their labels show the relative error between observed and predicted lesion sizes at each timepoint.

Two **solid lines** are displayed: the orange line represents the observed lesion sizes (ground truth), and the yellow 
line shows the predicted lesion sizes estimated by the selected segmentation model. Each point on these lines 
corresponds to a scan at a specific timepoint. The closer the two lines are, the more accurate the model is at 
capturing the lesion size for that particular time.

Between each pair of consecutive timepoints, **percentage values** are shown above the orange and yellow lines. These 
indicate the relative change in lesion size compared to the previous timepoint—positive values reflect lesion 
growth, while negative values represent shrinkage. This allows for an intuitive comparison of how the model interprets 
progression or treatment response compared to the actual clinical evolution.

To highlight discrepancies between predictions and ground truth, the panel also includes **dotted vertical blue lines** 
connecting the predicted and observed lesion sizes at each timepoint. Next to each line, a blue percentage indicates 
the relative error in volume estimation by the model. Larger percentages point to greater divergence from the ground 
truth, making it easy to spot timepoints where the model struggles.

---

All plots are interactive, powered by _Plotly_, allowing users to:

- Toggle datasets on and off
- Zoom and pan within plots
- Export high-resolution images
- Hover to inspect exact values

Whether you're debugging unexpected results or preparing figures for publication, this analysis mode is a core part of 
the AUDIT toolkit.
