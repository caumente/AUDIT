# BraTS 2024 Tutorial

This tutorial guides you step by step through preparing the BraTS 2024 dataset, organizing it, configuring feature 
extraction, and launching the interactive dashboard to explore your data using the AUDIT framework.

Unlike [BraTS 2025](BraTS_2025.md), this dataset includes a demographic mapping file containing valuable metadata such as glioma type, 
MRI scanner specifications, magnetic field strength, and patient demographics. This enables a deeper analysis not only 
exploring dataset structure and image-derived features but also uncovering potential biases or acquisition-related 
differences that may affect model performance.

AUDIT provides a unified environment to analyze, compare, and visualize these variations across patient cohorts, 
acquisition sites, and demographic groups.

References:

- [The 2024 Brain Tumor Segmentation (BraTS) Challenge: Glioma Segmentation on Post-treatment MRI](https://arxiv.org/abs/2405.18368)

- [The RSNA-ASNR-MICCAI BraTS 2021 Benchmark on Brain Tumor Segmentation and Radiogenomic Classification](https://arxiv.org/abs/2107.02314)

- [BraTS orchestrator : Democratizing and Disseminating state-of-the-art brain tumor image analysis](https://arxiv.org/abs/2506.13807)


!!! note

    The [annotation protocol](https://www.synapse.org/Synapse:syn64153130/wiki/631053) followed in this tutorial was: 
    Label 0: Background, Label 1: Non-enhancing tumor core, Label 2: surrounding non-enhancing FLAIR hyperintensity, 
    Label 3: Enhancing tumor, Label 4: resection cavity. However, we encourage users to check the protocol used in their datasets.

---

## 1. Prerequisites

Before starting, make sure you are familiar with the BraTS 2025 tutorial, as this guide assumes you already understand 
the fundamentals of AUDIT, such as environment setup, project structure, and configuration files.

We recommend using an isolated Anaconda environment with Jupyter Notebook and following the same project organization 
used in the previous tutorial.

The BraTS 2024 dataset is hosted on Synapse and **requires prior registration**. Please follow the [official 
instructions](https://www.synapse.org/Synapse:syn64153130/wiki/) from the challenge and to BraTS 2024
[Data Access](https://www.synapse.org/Synapse:syn64377310) section to download the data. 

Once downloaded and unzipped, store the training and additional training sets in a directory called 
`.datasets/BraTS_2024`. The metadata file must be stored in the project root. The project structure should look like 
this before starting:

```
brats2024_project/
├── datasets/
├──── BraTS_2024/
├─────── BraTS-GLI-00005-100/
├─────── BraTS-GLI-00005-101/
├─────── .....
├── config/
├── outputs/
├── logs/
├── BraTS-PTG supplementary demographic information and metadata.xlsx
```


---

## 2. Exploring the metadata

Before working with the imaging data, it is useful to explore the metadata. The BraTS 2024 demographic spreadsheet 
includes variables such as acquisition site, magnetic field strength, scanner manufacturer, patient age, sex, and 
glioma type - all of which can later be used to stratify analyses and investigate dataset heterogeneity.

Let’s begin by loading the file in a pandas DataFrame and take a first look:

```python
import pandas as pd
mapping = pd.read_excel("./BraTS-PTG supplementary demographic information and metadata.xlsx")
mapping.head(4)
```

This will give you a table like this:

| BraTS Subject ID     | Site | Site Subject ID | Annotator 1 | Approver 1 | Train/Test/Validation | Magnetic Field Strength | Manufacturer | Patient's Age | Patient's Sex | Glioma type       |
|----------------------|------|-----------------|-------------|------------|-----------------------|-------------------------|--------------|---------------|---------------|-------------------|
| BraTS-GLI-00005-100  | UCSF | 1002251         | NaN         | AMR        | Train                 | 3.0                     | GE           | 50.0          | M             | Oligodendroglioma |
| BraTS-GLI-00005-101  | UCSF | 1002252         | NaN         | AMR        | Train                 | 3.0                     | GE           | 50.0          | M             | Oligodendroglioma |
| BraTS-GLI-00006-100  | UCSF | 1001751         | BKKF        | JDR        | Train                 | 3.0                     | GE           | 39.0          | F             | Glioblastoma      |
| BraTS-GLI-00006-101  | UCSF | 1001752         | BKKF        | JDR        | Train                 | 3.0                     | GE           | 39.0          | F             | Glioblastoma      |


Each patient record is linked to a specific site and scanner configuration. Later, you can use this information to 
partition the dataset and perform site-wise or scanner-wise analyses.

For this tutorial, we will focus on the training and additional training subsets, excluding validation data.

```python
df = mapping[mapping["Train/Test/Validation "].isin(["Train", "Train-additional"])]
```

## 3. Organizing the dataset by site

To facilitate comparisons between different acquisition centers, we will reorganize the dataset into site-specific 
folders.  The function below automates the process by reading the metadata and copying each subject folder into the 
appropriate subdirectory. However, we  encourage users to perform their own analyses, exploring splitting by glioma 
type, magnetic field strength, manufacturer, and other variables.

The goal is to show how AUDIT can help you better understand your dataset and perform a more accurate evaluation of
segmentation models and MRI cohorts.

Let's create a function to move each patient into their corresponding folder, instead of keeping all of them grouped 
in a single directory.

```python
import os
import shutil

def organize_patients(df, column, input_dir, output_dir):
    """
    Organize patient folders into subfolders based on a DataFrame column.

    Parameters
    ----------
    df : pd.DataFrame
        Metadata DataFrame (must contain 'BraTS Subject ID').
    column : str
        Column name to organize by (e.g., 'Site', 'Manufacturer', 'Glioma type').
    input_dir : str
        Directory containing all patient folders (e.g., 'BraTS_2024').
    output_dir : str
        Directory where organized folders will be created (e.g., 'BraTS_2024_by_site').
    """

    os.makedirs(output_dir, exist_ok=True)

    for _, row in df.iterrows():
        subject = row["BraTS Subject ID"]
        category = str(row[column])  # subfolder name

        # Create category subfolder if it doesn’t exist
        category_folder = os.path.join(output_dir, category)
        os.makedirs(category_folder, exist_ok=True)

        # Source patient folder/file
        subject_path = os.path.join(input_dir, subject)
        dest_path = os.path.join(category_folder, subject)

        if os.path.exists(subject_path):
            if os.path.isdir(subject_path):
                shutil.copytree(subject_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(subject_path, dest_path)
        else:
            print(f"Subject {subject} not found in {input_dir}")

    print(f"Organization completed in {output_dir}")
```

This function allows you to organize patients into separate directories and can be reused for any other analysis you 
want to perform with the BraTS 2024 dataset. Run the following code to organize your data by acquisition site:

```python
input_dir = "./datasets/BraTS_2024"
output_dir = "./datasets/BraTS_2024_by_site"

organize_patients(df, column="Site", input_dir=input_dir, output_dir=output_dir)
```

Ready! After running this, your project structure will look like:

```
brats2024_project/
├── datasets/
├──── BraTS_2024_by_site/
├────── Duke/
├──────── Duke-02060-100/
├──────── Duke-02060-101/
├──────── .....
├────── Indiana/
├────── Missouri/
├────── UCSD/
├────── UCSF/
├── config/
├── outputs/
├── logs/
├── BraTS-PTG supplementary demographic information and metadata.xlsx
```

To be able to take advantage of all functionalities of AUDIT, for instance the connectivity with ITK-Snap toolkit, we
recommend locating the sequences and masks under the same folder, and predictions for each model under another. Then,
The project structure should be the following.

```
brats2024_project/
├── datasets/
├──── BraTS_2024_by_site/
├────── Duke/
├──────── Duke_images/
├────────── Duke-02060-100/
├────────── Duke-02060-101/
├────────── .....
├──────── Duke_segs/
├────────── model_1/
├──────────── Duke-02060-100_pred.nii.gz
├──────────── Duke-02060-101_pred.nii.gz
├────────── .....
├────────── model_2/
├──────────── Duke-02060-100_pred.nii.gz
├──────────── Duke-02060-101_pred.nii.gz
├────────── .....
├────── Indiana/
├────── Missouri/
├────── UCSD/
├────── UCSF/
├── config/
├── outputs/
├── logs/
├── BraTS-PTG supplementary demographic information and metadata.xlsx
```

## 4. Standardize folder and file naming

As in the BraTS 2025 tutorial, we need to standardize the folder and file names to ensure AUDIT compatibility. This 
includes replacing prefixes, updating sequence identifiers, and ensuring consistent use of underscores. Check
[BraTS 2025 tutorial](BraTS_2025.md) for more details.

### 4.1 Rename folders and files

We’ll first replace the `BraTS-GLI-` prefix with the site name for clarity.

```python
sites = ["Duke", "Indiana", "Missouri", "UCSD", "UCSF"]
for s in sites:
    rename_dirs(
        root_dir=os.path.join(output_dir, s),
        old_name="BraTS-GLI",
        new_name=s,
        safe_mode=False
    )
    
    rename_files(
        root_dir=os.path.join(output_dir, s),
        old_name="BraTS-GLI",
        new_name=s,
        safe_mode=False
    )
```

### 4.2 Standardize sequence

Additionally, to make the sequence names clearer and consistent, we will replace suffixes:

```python
old_names = ['-seg.nii.gz', '-t1c.nii.gz', '-t1n.nii.gz', '-t2f.nii.gz', '-t2w.nii.gz']
new_names = ['_seg.nii.gz', '_t1ce.nii.gz', '_t1.nii.gz', '_flair.nii.gz', '_t2.nii.gz']
sites = ["Duke", "Indiana", "Missouri", "UCSD", "UCSF"]

for s in sites:
    for o, n in zip(old_names, new_names):
        rename_files(
            root_dir=os.path.join(output_dir, s),
            old_name=o,
            new_name=n,
            safe_mode=False
        )
```

### 4.3 Replace dashes with underscores (optional)

Finally, to ensure consistent naming conventions, we replace all `-` characters with `_`:

```python
for s in sites:
    rename_files(root_dir=root_dir=os.path.join(output_dir, s), old_name="-", new_name="_", safe_mode=False)
    rename_dirs(root_dir=root_dir=os.path.join(output_dir, s), old_name="-", new_name="_", safe_mode=False)
```

---

## 5. Run feature extraction

Now that the datasets are ready, let’s configure the feature extraction. AUDIT takes advantage of YAML configuration 
files for extracting features and metrics and running the app. All of them have been created automatically inside 
the `configs/` at the time of generating the project structure. The one we need to edit to run the feature extraction 
is named `feature_extraction.yaml`. 

Here we provide the config file needed for this project. In it, paths to datasets, sequences names, labels mapping, 
features to extract, and output paths need to be defined.:

```yaml
# Paths to all the datasets
data_paths:
  Duke: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_images/'
  Indiana: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Indiana/Indiana_images/'
  Missouri: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Missouri/Missouri_images/'
  UCSD: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/UCSD/UCSD_images/'
  UCSF: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/UCSF/UCSF_images/'

# Sequences available
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  NETC: 1
  SNFH: 2
  ET: 3
  RC: 4

# List of features to extract
features:
  statistical: true
  texture: true
  spatial: true
  tumor: true

# Output paths
output_path: '/home/usr/brats2024_project/outputs/features'
logs_path: '/home/usr/brats2024_project/logs/features'

# Resources
cpu_cores: 4
```

Run feature extraction by using the following command:

```bash
auditapp feature-extraction --config /home/usr/projects/configs/feature_extraction.yaml
```

After execution, `/home/usr/brats2024_project/outputs/features` will contain the extracted features for all the datasets.

!!! danger "Important"
    All paths must be absolute. Otherwise, AUDIT may fall back to its internal default config files.

---

## 6. Launch the dashboard (without predictions)

Once features are extracted, we can explore them using the web app. We should edit the config file named `app.yaml` and 
adapt it as follows:

```yaml
# Sequences available
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  NETC: 1
  SNFH: 2
  ET: 3
  RC: 4

# Root paths
datasets_path: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site'
features_path: '/home/usr/brats2024_project/outputs/features'
metrics_path: '/home/usr/brats2024_project/outputs/metrics'

# Raw datasets
raw_datasets:
  Duke: "${datasets_path}/Duke/Duke_images"
  Indiana: "${datasets_path}/Indiana/Indiana_images"
  Missouri: "${datasets_path}/Missouri/Missouri_images"
  UCSD: "${datasets_path}/UCSD/UCSD_images"
  UCSF: "${datasets_path}/UCSF/UCSF_images"

# Feature extraction CSVs
features:
  Duke: "${features_path}/extracted_information_Duke.csv"
  Indiana: "${features_path}/extracted_information_Indiana.csv"
  Missouri: "${features_path}/extracted_information_Missouri.csv"
  UCSD: "${features_path}/extracted_information_UCSD.csv"
  UCSF: "${features_path}/extracted_information_UCSF.csv"


# Metric extraction CSVs
metrics:

# Model predictions
predictions:

```

Launch the app with:

```bash
auditapp run-app --config /home/usr/projects/configs/app.yaml
```

Now it’s time to explore the datasets!

Keep in mind that some feature types may influence generalization across cohorts more than others. For example, while 
the statistical features appear quite similar between the datasets, we encourage you to dive deeper into the data, 
experiment with different feature sets, and challenge your models to reach the next level of performance.

> ![Univariate feature analysis](../assets/tutorials/brats2024_t1_max_intensity_l.png#only-light)
> ![Univariate feature analysis](../assets/tutorials/brats2024_t1_max_intensity_d.png#only-dark)
> *Figure 1:* Univariate feature analysis mode. Maximum pixel intensity distribution for T1 sequence.


If everything has been set up correctly — especially making sure to include the patients (original sequences and masks)
within the dataset_images directory (e.g., datasets/Duke/Duke_images/), and ITK has been installed properly as suggested in the documentation,
then it is possible to click on any of the points of interest and explore them directly in ITK-SNAP.
In our case, we clicked on the patient Indiana-03062-100.


> ![ITK-SNAP by clicking on a point](../assets/tutorials/brats2024_itksnap_l.png#only-light)
> ![ITK-SNAP by clicking on a point](../assets/tutorials/brats2024_itksnap_d.png#only-dark)
> *Figure 2:* Subject Indiana-03062-100 exploration directly on ITK-SNAP by clicking on a point from the boxplot shown in Figure 1.

---


## 7. Perform inference

In addition to analyzing data distributions, studying correlations, identifying anomalous subjects, and many other 
analyses, one of AUDIT's main functionalities is the evaluation of AI medical segmentation models. To perform inference, 
we used the models presented at MICCAI 2025, specifically the top 4 ranked models in the Adult Glioma Segmentation 
(Pre & Post-Treatment) challenge.

For this purpose, we leveraged the [brats](https://github.com/BrainLesion/BraTS) library, which contains the Docker 
containers for each of the models:

| Year | Rank | Authors | Paper | Available | Model ID |
|------|------|---------|-------|-----------|----------|
| 2025 | 1st | Ishika Jain, et al. | N/A | ❌ | BraTS25_1 |
| 2025 | 2nd | Qu Lin, et al. | N/A | ✅ | BraTS25_2 |
| 2025 | 3rd | Liwei Jin, et al. | N/A | ✅ | BraTS25_3A |
| 2025 | 3rd | Adrian Celaya, et al. | N/A | ❌ | BraTS25_3B |

After performing inference on the 5 subdatasets (Duke, Indiana, Missouri, UCSD, and UCSF) with each of the 4 models, 
your project structure should look like the following, for example for subject Duke-02060-100:

```
brats2024_project/
├── datasets/
├──── BraTS_2024_by_site/
├────── Duke/
├────── Duke_images/
├────────── Duke-02060-100/
├──────────── Duke-02060-100_flair.nii.gz
├──────────── Duke-02060-100_t1.nii.gz
├──────────── Duke-02060-100_t2.nii.gz
├──────────── Duke-02060-100_t1ce.nii.gz
├──────────── Duke-02060-100_seg.nii.gz
├────────── .....
├────── Duke_seg/
├────────── BraTS25_1/
├──────────── Duke-02060-100/
├────────────── Duke-02060-100_pred.nii.gz
├──────────── .....
├────────── BraTS25_2/
├────────── BraTS25_3A/
├────────── BraTS25_3B/
```

!!! danger "Important"
    The suffixes **_seg** and **_pred** are reserved keywords within AUDIT and are necessary for metric calculation.

## 8. Run metric extraction

Now that the datasets are ready, let's configure metric extraction. Just as we did previously, we now need to configure 
the file named `metric_extraction.yaml`.

Here we provide the config file needed to extract metrics for the Duke dataset. Paths to datasets, sequence names, 
label mappings, metrics to compute, and output paths need to be defined. The same configuration file should be prepared 
for each of the other datasets.

```yaml
# Path to the raw dataset
data_path: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_images'

# Paths to model predictions
model_predictions_paths:
  BraTS25_1: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_1'
  BraTS25_2: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_2'
  BraTS25_3A: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_3A'
  BraTS25_3B: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/Duke_seg/BraTS25_3B'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  NETC: 1
  SNFH: 2
  ET: 3
  RC: 4

# List of metrics to compute
metrics:
  dice: true
  jacc: true
  accu: true
  prec: true
  sens: true
  spec: true
  haus: true
  size: true

# Library used for computing all the metrics
package: audit

# Path where output metrics will be saved
output_path: '/home/usr/brats2024_project/outputs/metrics'
filename: 'Duke'
logs_path: '/home/usr/brats2024_project/logs/metric'

# Resources
cpu_cores: 4
```

Run metric extraction by using the following command:

```bash
auditapp metric-extraction --config /home/usr/projects/configs/metric_extraction.yaml
```

After execution, `/home/usr/brats2024_project/outputs/metrics` will contain the extracted metrics for all the datasets.
    

!!! danger "Important"
    All paths must be absolute. Otherwise, AUDIT may fall back to its internal default config files.

## 9. Launch the dashboard (with predictions)

Now that we have generated all predictions and extracted both features and metrics, we can relaunch the dashboard as 
we did in step 6. However, in this case we must include new lines in our configuration file to enable reading of the
predictions.

Here we provide the remaining portion of the configuration file started in section 6. Users should concatenate this 
information with the previous configuration.

```yaml
# Paths for metric extraction CSV files
metrics:
  Duke: "${metrics_path}/extracted_information_Duke.csv"
  Indiana: "${metrics_path}/extracted_information_Indiana.csv"
  Missouri: "${metrics_path}/extracted_information_Missouri.csv"
  UCSD: "${metrics_path}/extracted_information_UCSD.csv"
  UCSF: "${metrics_path}/extracted_information_UCSF.csv"

# Paths for models predictions
predictions:
  Duke:
    BraTS2025_1: "${datasets_path}/Duke/Duke_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/Duke/Duke_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/Duke/Duke_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/Duke/Duke_seg/BraTS25_3B"
  Indiana:
    BraTS2025_1: "${datasets_path}/Indiana/Indiana_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/Indiana/Indiana_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/Indiana/Indiana_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/Indiana/Indiana_seg/BraTS25_3B"
  Missouri:
    BraTS2025_1: "${datasets_path}/Missouri/Missouri_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/Missouri/Missouri_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/Missouri/Missouri_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/Missouri/Missouri_seg/BraTS25_3B"
  UCSD:
    BraTS2025_1: "${datasets_path}/UCSD/UCSD_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/UCSD/UCSD_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/UCSD/UCSD_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/UCSD/UCSD_seg/BraTS25_3B"
  UCSF:
    BraTS2025_1: "${datasets_path}/UCSF/UCSF_seg/BraTS25_1"
    BraTS2025_2: "${datasets_path}/UCSF/UCSF_seg/BraTS25_2"
    BraTS2025_3A: "${datasets_path}/UCSF/UCSF_seg/BraTS25_3A"
    BraTS2025_3B: "${datasets_path}/UCSF/UCSF_seg/BraTS25_3B"
```

Launch the app again with:

```bash
auditapp run-app --config /home/usr/projects/configs/app.yaml
```

## 10. Model evaluation

AUDIT presents different analysis modes to evaluate model behavior, from high-level granularity down to fine-grained 
details at the patient and region level. Some of the analyses we can perform include the following:

### 10.1 Segmentation error matrix

The segmentation error matrix allows you to analyze in detail which regions your model confuses. It is a pseudo-confusion 
matrix normalized at the ground truth level. For more details about how this analysis mode works, check out the 
[documentation](./../analysis_modes/segmentation_error.md).

> ![Segmentation error matrix for Duke dataset and BraTS2025_1 model](../assets/tutorials/brats2024_segmentation_matrix_l.png#only-light)
> ![Segmentation error matrix for Duke dataset and BraTS2025_1 model](../assets/tutorials/brats2024_segmentation_matrix_d.png#only-dark)
> *Figure 3:* Segmentation error matrix for the Duke dataset and BraTS2025_1 model.

The matrix is analyzed at a global level, encompassing all errors made by the model at a high level throughout the 
entire dataset. The main problem of the model is confusing Background with the SNFH region. Therefore, developers 
should focus on finding strategies to minimize this weakness. The next most frequent confusion is predicting Background 
when the actual label is RC. However, it's important to note that this evaluation is done as a percentage normalized 
at the actual region level, so it must be interpreted carefully.

If we focus on a specific subject, for example patient Duke-02060-100, we can analyze whether this same pattern holds 
in absolute terms:

> ![Segmentation error matrix for patient Duke-02060-100 from Duke dataset and BraTS2025_1 model](../assets/tutorials/brats2024_segmentation_matrix_patient_l.png#only-light)
> ![Segmentation error matrix for patient Duke-02060-100 from Duke dataset and BraTS2025_1 model](../assets/tutorials/brats2024_segmentation_matrix_patient_d.png#only-dark)
> *Figure 4:* Segmentation error matrix for patient Duke-02060-100 from the Duke dataset and BraTS2025_1 model.

The behavior of confusing Background and SNFH that we observed at the dataset level also holds in absolute terms for 
this specific patient. A total of 2,905 voxels were labeled as Background when they were actually voxels labeled as 
tumoral by the medical experts (SNFH). However, for this specific patient, there are a total of 2,106 voxels that were 
labeled as Background again, but actually belonged to the ET region.

This is why it's crucial to understand not only the general behavior of the model, but also the specific cases. Now 
that we know that for this specific patient the ET region was incorrectly labeled, we should analyze in detail the MRI 
characteristics of this patient to see if there is any peculiarity that makes that region especially difficult to segment.

### 10.2 Single model performance

Analyzing model performance as a function of different characteristics allows us to understand whether our model has 
any bias. For example, we can answer questions such as: does my model perform better when predicting tumors that are 
far from the brain's center of mass, or does our model predict better for tumors belonging to a specific pathology? 
For more details about how this analysis mode works, check out the [documentation](./../analysis_modes/single_model.md).

Ideally, what we would expect to see is a plot where we don't visualize any specific trend, indicating that there is 
no bias. That is precisely what we observe in the following figure:

> ![Single model performance analysis for BraTS2025_1 model](../assets/tutorials/brats2024_single_model_performance_l.svg#only-light)
> ![Single model performance analysis for BraTS2025_1 model](../assets/tutorials/brats2024_single_model_performance_d.svg#only-dark)
> *Figure 5:* Performance analysis of the BraTS2025_1 model as a function of tumor location for each subset.

As we can see, the model has been trained with data that is robust enough in terms of tumor location not to have 
problems with different locations.

!!! note
    We recommend that users conduct their own analyses and draw their own conclusions, as certain correlations may not 
    be linear, and transformations such as logarithmic could reveal hidden trends.


### 10.3 Pair-wise model performance

The BraTS competition awarded third place to two different models, here called BraTS25_3A and BraTS25_3B on the private 
test set. We don't have access to it and are evaluating the models on the training set itself. However, this is 
sufficient for our demonstrative purposes.

#### 10.3.1 Pair-wise model performance - Aggregated view

Let's make a comparison taking the BraTS25_3A model as the baseline model and BraTS25_3B as the benchmark. In our case,
having the dataset divided by Site, we can analyze the differences individually. We will use the Dice metric as it is 
the most widely reported in medical segmentation problems.

> ![Pairwise model performance analysis for BraTS25_3A and BraTS25_3B models](./../assets/tutorials/brats2024_agg_pairwise_model_performance_l.png#only-light)
> ![Pairwise model performance analysis for BraTS25_3A and BraTS25_3B models](./../assets/tutorials/brats2024_agg_pairwise_model_performance_d.png#only-dark)
> *Figure 6:* Pairwise model performance comparison between BraTS25_3A and BraTS25_3B models for the Duke subset.

On average, the BraTS 3B model improved the performance of the BraTS 3A model by up to 1.42% for the Dice metric. The 
improvement came mainly from better segmentation of the RC region, and to a lesser extent from the NETC and ET regions. 
However, the model worsened its performance for the SNFH region by around 1%.

AUDIT also provides an estimation of whether the differences are statistically significant. For example, if we select 
the Missouri subset, we can verify that the average differences between both models are 0.09%, apparently a minimal 
difference. When performing the Wilcoxon signed-rank statistical test due to the violation of parametric assumptions, 
it is verified that there are no significant differences to reject the null hypothesis. Therefore, on this specific 
subset, the behavior of both models is similar.

> ![Statistical test results for BraTS25_3A and BraTS25_3B models](./../assets/tutorials/brats2024_statistical_test_l.png#only-light)
> ![Statistical test results for BraTS25_3A and BraTS25_3B models](./../assets/tutorials/brats2024_statistical_test_d.png#only-dark)
> *Figure 7:* Statistical test results between models BraTS25_3A and BraTS25_3B to verify if the differences are statistically significant.


#### 10.3.4 Pair-wise model performance - Disaggregated view

In general, artificial intelligence models in the field of medical imaging are analyzed at a high level, comparing 
general metrics such as mean or median, and sometimes not even providing a measure of variance. This is why it's 
essential to understand how the model behaves at the patient level, why the model fails in some specific cases, 
and to ensure that the new version of the model we develop not only achieves better average results but also 
generalizes well and doesn't make significant errors on certain patients that we were already able to segment correctly.

With AUDIT we can analyze model performance at the patient level. We can obtain a Top-K patients to analyze either by 
name, by baseline model performance, benchmark model performance, sort ascending or descending, etc. Let's compare the 
performance of models BraTS_3A and BraTS_3B on the UCSF subset.


> ![Pairwise patient-level performance analysis for BraTS25_3A and BraTS25_3B models](./../assets/tutorials/brats2024_pairwise_per_patient_l.png#only-light)
> ![Pairwise patient-level performance analysis for BraTS25_3A and BraTS25_3B models](./../assets/tutorials/brats2024_pairwise_per_patient_d.png#only-dark)
> *Figure 8:* Comparison results between models BraTS25_3A and BraTS25_3B at the subject level.

 
As can be observed, BraTS25_3B, our benchmark, has clearly improved the results obtained by baseline BraTS25_3A in cases 
UCSF-00005-100 and UCSF-00005-101, going from values around 0.70 to values of 0.94. This same exercise should be done 
for those patients for which performance was poor, to understand what the weaknesses of our model are.


---

## 11. Conclusions

Throughout this tutorial we have presented some of the features that AUDIT provides. It not only allows analyzing 
differences in distributions, but its strength lies in model evaluation and low-level comparison—analyses that often 
go unnoticed when presenting results in the field of medical imaging.


