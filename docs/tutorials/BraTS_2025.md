# BraTS 2025 Tutorial

This tutorial guides you step-by-step through preparing the **BraTS 2025 dataset**, organizing it, extracting features, 
and launching the interactive dashboard to explore your data—all powered by the **AUDIT framework**.

!!! note "Working with limited resources?"
    If you have computational or storage constraints, you can skip the feature extraction entirely! Pre-extracted features 
    for both datasets are publicly available in the AUDIT GitHub repository. Simply 
    [download](https://github.com/caumente/AUDIT/tree/main/outputs/features) the CSV files and jump directly to Section 6.

References:

- [The 2024 Brain Tumor Segmentation (BraTS) Challenge: Glioma Segmentation on Post-treatment MRI](https://arxiv.org/abs/2405.18368)

- [The RSNA-ASNR-MICCAI BraTS 2021 Benchmark on Brain Tumor Segmentation and Radiogenomic Classification](https://arxiv.org/abs/2107.02314)

!!! warning

    The [annotation protocol](https://www.synapse.org/Synapse:syn64153130/wiki/631053) followed in this tutorial was: 
    Label 0: Background, Label 1: Necrotic core, Label 2: Edema, Label 3: Enhancing tumor. However, we encourage users 
    to check the protocol used in their datasets.

---

## 1. Prerequisites & Installation

Before working with the dataset, we need to set up a clean environment. This ensures that all dependencies are properly
managed and won't conflict with other Python packages you may have installed on your system.

### 1.1 Create a new environment

We recommend creating a new conda environment to avoid conflicts with other packages. Conda provides excellent package 
management and environment isolation:

```python
conda create -n audit_env python=3.10
conda activate audit_env
```

This creates an isolated Python 3.10 environment named audit_env. Python 3.10 is the recommended version for AUDIT, as 
it provides the best compatibility with all dependencies.

### 1.2 Install required packages

Install the core AUDIT package and Jupyter-related dependencies. The AUDIT package includes all necessary tools for 
feature extraction, metric computation, and visualization:

```python
pip install auditapp
pip install ipykernel jupyter
```

### 1.3 Register kernel for Jupyter

Register the environment so it appears as an option in Jupyter Notebook. This step is crucial for ensuring that Jupyter 
can access the packages installed in your conda environment:

```python
python -m ipykernel install --user --name=audit_env --display-name "Python (audit_env)"
```

This command registers your environment with Jupyter, making it available in the kernel selection menu. The 
--display-name parameter determines what you'll see in the Jupyter interface.

Now, launch Jupyter Notebook:

```python
jupyter notebook
```

When opening a notebook, select the kernel "Python (audit_env)" from the Kernel menu 
(Kernel → Change kernel → Python (audit\_env)). This ensures that all code cells execute within your AUDIT environment 
with access to all installed packages.

!!! tip
    Check out our [installation guide](https://caumente.github.io/AUDIT/getting_started/installation/) if you need more
    detailed instructions or troubleshooting tips.

---

## 2. Download the BraTS 2025 data

The BraTS 2025 dataset is one of the most comprehensive brain tumor segmentation datasets available, containing 
multimodal MRI scans with expert annotations. Understanding how to properly access and organize this data is essential 
for working with AUDIT.

The BraTS 2025 dataset is hosted on Synapse and **requires prior registration**. Please follow the [official 
instructions](https://www.synapse.org/Synapse:syn64153130/wiki/) from the challenge and to BraTS 2025
[Data Access](https://www.synapse.org/Synapse:syn64377310) section to download the data. For this tutorial, we will take advantage of both the training and 
validation datasets. 


After downloading, you'll receive compressed archives (typically .zip or .tar.gz files). For consistency with this 
tutorial and to ensure that all subsequent commands work without modification, rename the extracted folders as follows:

- Training dataset → BraTS2025_train
- Validation dataset → BraTS2025_val

---

## 3. Project structure

A well-organized project structure is fundamental to working efficiently with AUDIT. The framework expects specific 
directories for datasets, configurations, outputs, and logs. Let's set this up properly.

### 3.1 Create base project directory

Open your terminal and create a new folder for your project. This will serve as the root directory for all 
AUDIT-related work:

```python
mkdir brats2025_project
cd brats2025_project
```

You can name this folder anything you prefer, but for consistency with this tutorial, we'll use brats2025_project. 
All subsequent paths will be relative to this directory.

### 3.2 Initialize AUDIT project structure

AUDIT library requires a specific base structure for the project to function correctly. This structure separates 
raw data, configurations, outputs, and logs into organized directories. To create this structure, let's start by 
creating a new Jupyter notebook in your project directory and importing some necessary functions from 
the __file_manager__ module.

Open Jupyter (if not already open), create a new notebook and import the required utilities:

```python
from audit.utils.commons.file_manager import (
    create_project_structure,
    list_dirs,
    rename_files,
    rename_dirs
)
```

Now, let's create the project folder hierarchy by running the following command. Define the base path where you want 
to create the project structure (in this case, the current directory):


```python
create_project_structure(base_path="./")
```

After executing this command, you should see the following structure in your project directory:

```
brats2025_project/
├── datasets/
├── config/
├── outputs/
├── logs/
```


### 3.3 Organize your datasets

Now that we have the proper directory structure, it's time to move the downloaded BraTS 2025 datasets into the project.
Unzip the folders and move both datasets, training and validation, into your project’s `./datasets/` folder.

After this step, your project structure should look like:

```
brats2025_project/
├── datasets/
│   ├── BraTS2025_train/
│   │   ├── BraTS-GLI-00000-000/
│   │   ├── BraTS-GLI-00002-000/
│   │   └── ...
│   └── BraTS2025_val/
│       ├── BraTS-GLI-00000-000/
│       ├── BraTS-GLI-00002-000/
│       └── ...
├── config/
├── outputs/
└── logs/
```

Each subject folder contains multiple NIfTI files (.nii.gz format) representing different MRI sequences 
(T1, T1CE, T2, FLAIR) and the segmentation mask.

In your Jupyter notebook, define Python variables pointing to your datasets. Using variables makes it easier to 
reference these paths throughout your workflow:

```python
train_data_path = "./datasets/BraTS2025_train/"
val_data_path = "./datasets/BraTS2025_val/"
```

Verify that the datasets are accessible and contain the expected data:

```python
# Preview first subfolders
print(list_dirs(train_data_path)[:10])

['BraTS-GLI-00000-000', 'BraTS-GLI-00002-000', ...]
```


---

## 4. Standardize folder and file naming

To ensure compatibility with AUDIT and maintain consistency across your project, we need to standardize the naming 
conventions for both folders and files. The BraTS dataset uses specific naming patterns that we'll modify to be more 
explicit and aligned with AUDIT's expectations.

### 4.1 Rename folders


We will replace the generic prefix BraTS-GLI- with dataset-specific names (BraTS2025_train or BraTS2025_val). This 
makes it immediately clear which dataset each subject belongs to, which is especially important when analyzing 
results or comparing features across datasets.

The renaming functions from AUDIT contain several parameters that provide fine-grained control over the renaming process:

- safe_mode: When set to True, performs a dry run that shows what would be renamed without actually changing anything. This is highly recommended for first-time users or when working with new datasets.
- verbose: When set to True, prints detailed information about each rename operation, allowing you to see exactly what's being changed.
- recursive: Controls whether to search subdirectories (useful for complex dataset structures).

You can check out the complete documentation for these functions in the file manager module from 
the [API reference](../API_reference/utils/file_manager.md).


Once you've verified that the preview looks correct and you're ready to proceed, run the actual renaming commands:

```python
rename_dirs(
    root_dir=train_data_path,
    old_name="BraTS-GLI",
    new_name="BraTS2025_train",
    safe_mode=False
)

rename_dirs(
    root_dir=val_data_path,
    old_name="BraTS-GLI",
    new_name="BraTS2025_val",
    safe_mode=False
)
```

### 4.2 Rename files

AUDIT also provides analogous functions for file manipulation. The file renaming process is similar to folder renaming, 
but it operates on the individual files within each subject directory (the NIfTI image files and segmentation masks).

Just as with folders, we'll replace the BraTS-GLI prefix with dataset-specific identifiers:

```python
rename_files(
    root_dir=train_data_path,
    old_name="BraTS-GLI",
    new_name="BraTS2025_train",
    safe_mode=False
)

rename_files(
    root_dir=val_data_path,
    old_name="BraTS-GLI",
    new_name="BraTS2025_val",
    safe_mode=False
)
```

This operation recursively processes all files within the dataset directories, ensuring consistent naming throughout 
your project.

### 4.3 Standardize sequences

Beyond the dataset prefixes, we also need to standardize the MRI sequence naming conventions. The original BraTS data 
uses abbreviations that may not be immediately clear or consistent with other datasets you might work with. Let's make 
the sequence names clearer and more explicit.

Original naming → Standardized naming:

- -seg.nii.gz → _seg.nii.gz (segmentation mask)
- -t1c.nii.gz → _t1ce.nii.gz (T1 contrast-enhanced)
- -t1n.nii.gz → _t1.nii.gz (T1 native/non-contrast)
- -t2f.nii.gz → _flair.nii.gz (FLAIR sequence)
- -t2w.nii.gz → _t2.nii.gz (T2-weighted)

```python
old_names = ['-seg.nii.gz', '-t1c.nii.gz', '-t1n.nii.gz', '-t2f.nii.gz', '-t2w.nii.gz']
new_names = ['_seg.nii.gz', '_t1ce.nii.gz', '_t1.nii.gz', '_flair.nii.gz', '_t2.nii.gz']

for root_path in [train_data_path, val_data_path]:
    for o, n in zip(old_names, new_names):
        rename_files(
            root_dir=root_path,
            old_name=o,
            new_name=n,
            safe_mode=False
        )
```


### 4.4 Replace dashes with underscores (optional)

Finally, for consistency, we replace all `-` characters with `_`:

```python
for root_path in [train_data_path, val_data_path]:
    rename_files(root_dir=root_path, old_name="-", new_name="_", safe_mode=False)
    rename_dirs(root_dir=root_path, old_name="-", new_name="_", safe_mode=False)
```

After this step, a typical subject folder will contain:

```
BraTS2025_train_00000_000/
├── BraTS2025_train_00000_000_t1.nii.gz       # T1-weighted
├── BraTS2025_train_00000_000_t1ce.nii.gz     # T1 contrast-enhanced
├── BraTS2025_train_00000_000_t2.nii.gz       # T2-weighted
├── BraTS2025_train_00000_000_flair.nii.gz    # FLAIR
└── BraTS2025_train_00000_000_seg.nii.gz      # Segmentation mask
```

If your output matches this format, congratulations! Your dataset is now properly standardized and ready for 
feature extraction.

---

## 5. Run feature extraction

Now that the datasets are properly organized and standardized, we can proceed to the feature extraction phase. This is
where AUDIT demonstrates its power by automatically computing a comprehensive set of radiomic and morphological 
features from your medical images.


### 5.1 Understanding AUDIT configuration files

AUDIT takes advantage of YAML configuration files for all major operations, including feature extraction, metric 
computation, and running the web application. 

When you created the project structure in Section 3, AUDIT automatically generated template configuration files in the 
`config/` directory. These templates contain sensible defaults, but we need to customize them for the BraTS 2025 dataset.
The configuration file we need to edit for feature extraction is named `feature_extraction.yaml.`


Open `config/feature_extraction.yaml` in your preferred text editor. Here's the complete configuration needed for this 
project, with detailed explanations for each section:

```yaml
# Paths to all the datasets
# IMPORTANT: These MUST be absolute paths, not relative paths
data_paths:
  BraTS2025_train: '/home/usr/brats2025_project/datasets/BraTS2025_train/'
  BraTS2025_val: '/home/usr/brats2025_project/datasets/BraTS2025_val/'

# Sequences available in your dataset
# These identifiers must match the suffixes in your standardized filenames
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values in the segmentation masks
# These values come from the BraTS challenge specification
labels:
  BKG: 0
  EDE: 2
  ENH: 3
  NEC: 1

# List of features to extract
# Set to 'true' to enable each feature category
features:
  statistical: true
  texture: true
  spatial: true
  tumor: true

# Output paths for extracted features and logs
# Again, these should be absolute paths
output_path: '/home/usr/brats2025_project/outputs/features'
logs_path: '/home/usr/brats2025_project/logs/features'

# Resource allocation
# Adjust cpu_cores based on your system (don't exceed your CPU count)
cpu_cores: 8
```

Once you've configured the YAML file with your absolute paths, you're ready to run the extraction. Open a terminal 
(not your Jupyter notebook) and execute:

```python
auditapp feature-extraction --config /home/usr/brats2025_project/configs/feature_extraction.yaml
```

After execution, `/home/usr/brats2025_project/outputs/features` will contain the extracted features for both training and 
validation datasets. The resulting CSV file will contain: Subject identifiers, features from each MRI sequence 
(T1, T2, T1CE, FLAIR), features for each label/region (background, edema, enhancing tumor, necrotic core), etc.

!!! warning "Important"
    All paths must be absolute. Otherwise, AUDIT may fall back to its internal default config files.


---

## 6. Launch the dashboard

Now comes the exciting part, exploring your data! Once features are extracted, AUDIT's interactive dashboard allows you 
to visualize feature distributions, identify outliers, compare datasets, and gain insights into your data quality and 
characteristics.

Just like feature extraction, the dashboard is configured using a YAML file. We need to edit `config/app.yaml` to tell 
AUDIT where to find your datasets, extracted features, and any metrics or predictions you might have.

Open `config/app.yaml` in your text editor and configure it as follows:

```yaml
# Sequences available in your dataset
# Must match the sequences defined in feature_extraction.yaml
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
# Must match the labels defined in feature_extraction.yaml
labels:
  BKG: 0
  EDE: 2
  ENH: 3
  NEC: 1

# Root paths
datasets_path: '/home/usr/brats2025_project/datasets'
features_path: '/home/usr/brats2025_project/outputs/features'
metrics_path: '/home/usr/brats2025_project/outputs/metrics'

# Raw datasets - Point to the directories containing your NIfTI files
# The dashboard uses these to load and display the actual MRI images
raw_datasets:
  BraTS2025_train: "${datasets_path}/BraTS2025_train"
  BraTS2025_val: "${datasets_path}/BraTS2025_val"

# Feature extraction CSVs - These contain all the extracted radiomic features for each subject
features:
  BraTS2025_train: "${features_path}/extracted_information_BraTS2025_train.csv"
  BraTS2025_val: "${features_path}/extracted_information_BraTS2025_val.csv"

# Metric extraction CSVs (optional)
metrics:

# Model predictions (optional)
predictions:
```

With your configuration file properly set up, you're ready to launch the dashboard. Open a terminal and execute:

```python
auditapp run-app --config /home/usr/brats2025_project/configs/app.yaml
```

Now it’s time to explore the datasets!

Keep in mind that some feature types may influence generalization across cohorts more than others. For example, while 
the statistical features appear quite similar between the datasets, we encourage you to dive deeper into the data, 
experiment with different feature sets, and challenge your models to reach the next level of performance.

> ![Univariate feature analysis](../assets/tutorials/brats2025_flair_median_intensity_l.png#only-light)
> ![Univariate feature analysis](../assets/tutorials/brats2025_flair_median_intensity_d.png#only-dark)
> *Figure 1:* Univariate feature analysis mode. Median pixel intensity distribution for FLAIR sequence.



---


