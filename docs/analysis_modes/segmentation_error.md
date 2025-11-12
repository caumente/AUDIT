# Segmentation error matrix

The **Segmentation Error Matrix** analysis in AUDIT provides an intuitive way to assess model performance at
the pixel level. It visualizes the confusion matrix of predicted vs. ground truth segmentations for each 
subject or aggregated across a dataset. This helps identify common misclassifications between tumor 
subregions and assess overall segmentation quality.

---

The goals of segmentation error matrix analysis are to:

- **Visualize systematic errors** across a dataset or individual subject.
- **Assess prediction quality for individual tumor subregions**, identifying which classes are most accurately segmented and which are often confused.
- **Spot model failure modes** not captured by summary metrics like Dice.

---

## 🎥 Demo video


Below is a short video that walks you through the segmentation error matrix mode interface:

[![Watch the video](https://img.youtube.com/vi/KW24py449bo/0.jpg)](https://youtu.be/KW24py449bo)

---

## ⚙️ User configuration

### 1. **Dataset selection**

In this mode, users can select a single dataset from the dropdown in the sidebar. Unlike other modes in AUDIT (such as 
the Multivariate analysis mode), the segmentation error matrix is not designed for multi-dataset comparison within the 
same view. Instead, its purpose is to provide a focused and detailed evaluation of how a segmentation model performs on 
a specific dataset by analyzing which tumor subregions are well segmented and which are commonly misclassified.

It is important that the segmentation labels and the ground truth labels must be aligned properly; otherwise, the 
analysis mode will not work correctly. You can follow this [tutorial](../tutorials/Lumiere_postprocessing.md) where it is explained how to modify the 
dataset labels to ensure proper alignment.

!!! warning
    This analysis mode compares the predicted segmentations directly against the ground truth labels.  
    Therefore, it can only be used when the original ground truth segmentations are available in the dataset.  
    If the dataset only contains predictions and lacks reference segmentations, the confusion matrix cannot be computed.


### 2. **Model selection**

In this step, users must select the segmentation model whose predicted outputs will be compared against the ground 
truth segmentations of the chosen dataset. This is crucial because the confusion matrix is computed by analyzing the 
pixel-wise agreement (or disagreement) between the model’s predictions and the ground truth labels.

The dropdown menu lists all available models that have generated predictions for the selected dataset. Selecting a 
model will load its prediction masks, which are then aligned with the ground truth segmentations to compute the 
pseudo-confusion matrix. Users can compare multiple models by changing this selection and observing differences in the 
matrices, which helps identify strengths and weaknesses in segmentation performance at the class level.

Models might differ in terms of architecture, training data, or preprocessing pipelines, so this step allows for 
flexible evaluation of any medical image segmentation model whose outputs are available in AUDIT.


### 3. **Select the subject ID to visualize**

Users have the option to select which subject(s) they want to analyze through the confusion matrix:

- **Specific subject**: Selecting an individual subject ID will display the confusion matrix for that single case. This 
    allows detailed inspection of how the model performed on that particular subject, helping to identify 
    subject-specific errors or unique segmentation challenges.

- **All**: Choosing _All_ aggregates the confusion matrices of every subject in the dataset into a single summary
    matrix. This aggregated view provides an overview of the model’s overall common error patterns across the entire
    cohort, smoothing out subject-level variability.

This flexibility enables both granular, case-by-case evaluation and broad, cohort-level assessment within the same 
interface.

---

## 📊 Visualization

The pseudo-confusion matrix shown in this mode is structured as follows:

- **Rows** represent the ground truth (true) labels, indicating the actual pixel classifications.  
- **Columns** represent the predicted labels output by the segmentation model, indicating the model’s pixel-wise classification.   
- **Diagonal cells** correspond to correctly classified pixels, where the predicted label matches the true label. Not shown, the matrix highlights only errors.
- **Off-diagonal cells** highlight misclassifications, where the predicted label differs from the true label.  

!!! info
    Darker colors in the matrix represent larger errors or higher misclassification rates by the model,  
    while lighter cells indicate fewer errors or better agreement between prediction and ground truth.  

The confusion matrix is normalized row-wise, meaning each row sums to 100%, which helps interpret the prediction 
distribution per true label. Since this is a pseudo-confusion matrix, pixels correctly classified are not indicated 
within the matrix. It is expected that the model classifies most of the regions correctly, so this analysis mode focuses 
on systematic errors instead.

!!! example
    For example, if the true label is "edema", the cells might be distributed as follows:  
    - A value of 70% in the "bkg" column means 70% of edema pixels were wrongly predicted as background.  
    - 25% in the "enh" column means 25% of edema pixels were wrongly predicted as enhancing tumor.  
    - 5% in the "nec" column means 5% of edema pixels were wrongly predicted as necrosis.


> ![Confusion matrix example](../assets/dashboards_examples/segmentation_matrix/single_subject_l.png#only-light)  
> ![Confusion matrix example](../assets/dashboards_examples/segmentation_matrix/single_subject_d.png#only-dark)
> *Figure 1:* Single subject confusion matrix for the nnUNet model on the BraTS2024_SSA dataset. The rows represent the true pixel labels. The columns represent the model's predicted labels. Darker cells indicate a higher percentage of misclassified pixels between true and predicted classes.

---

## 🧰 Additional options

### Normalization and averaging

- **Normalized per ground truth label** (enabled by default): normalizes each row so percentages sum to 100%, which
    makes it easier to interpret class-wise prediction behavior. When this button is disabled cells show the total
    number of misclassified pixels.

- **Averaged per number of subjects** (only available when "All" subjects are selected): computes the average
    pseudo-confusion matrix across all subjects.


!!! warning
    Be aware that the absolute pixel count of misclassified regions can be influenced by the voxel spacing of each MRI scan.  
    For this reason, it is highly recommended to register all datasets to a common reference space, so that voxel 
    sizes and orientations are standardized. Otherwise, cross-dataset comparisons can become difficult to interpret.

### ITK-SNAP integration

When a single subject is selected, users can launch ITK-SNAP to directly inspect the segmentation results in 3D.  
This launches the ground truth and predicted segmentations side by side.

!!! tip
    This feature is ideal for verifying segmentation quality when unusual confusion patterns appear in the matrix. It 
    can reveal issues like label swapping, partial segmentations, or preprocessing errors.

!!! warning
    ITK-SNAP must be installed and correctly configured in your system for this option to work.

---

All confusion matrices in AUDIT are fully interactive and support:

- Hover to reveal exact percentages
- Dynamic updates when selecting different datasets, models, or subjects

Whether you're debugging segmentation behavior or reporting evaluation results, this tool provides a clear and 
quantitative view into model errors and class-wise performance.

