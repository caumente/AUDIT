# BraTS 2025 Feature Extraction Tutorial

This tutorial will guide you step by step to prepare the **BraTS 2025 dataset**, organize it, configure the feature 
extraction, and finally launch the web app to explore the data. The workflow is based on the **AUDIT framework**.

---

## 1. Prerequisites & Installation

Before working with the dataset, we need to set up a clean environment.

### 1.1 Create a New Environment

We recommend creating a new conda environment to avoid conflicts with other packages:

```bash
conda create -n audit_env python=3.10
conda activate audit_env
```

### 1.2 Install Required Packages

Install the core AUDIT package and Jupyter-related dependencies:

```bash
pip install auditapp
pip install ipykernel jupyter
```

### 1.3 Register Kernel for Jupyter

Register the environment so it appears as an option in Jupyter Notebook:

```bash
python -m ipykernel install --user --name=audit_env --display-name "Python (audit_env)"
```

Now, start Jupyter Notebook:

```bash
jupyter notebook
```

When opening a notebook, select the kernel **Python (brats2025\_env)**.

!!! tip
    Check out our [installation guide](https://caumente.github.io/AUDIT/getting_started/installation/) if you need more
    detailed instructions or troubleshooting tips.

---

## 2. Download the BraTS 2025 Data

The BraTS 2025 dataset is hosted on **Synapse** and requires prior registration. Please follow the official 
instructions from the [BraTS 2025 Challenge](https://www.synapse.org/Synapse:syn64377310) to download the data.

After downloading, you will have training and validation datasets. For consistency, rename them to BraTS2025_train and
BraTS2025_val.

This ensures that the following steps work without additional modifications.

---

## 3. Project Structure

Open your terminal and create a new folder for your project. 

```bash
mkdir brats2025_project
cd brats2025_project
```

AUDIT library requires a specific base structure for the project. To do that, let's create a new notebook and import 
some necessary function from __file_manager__ module.

```python
from audit.utils.commons.file_manager import (
    create_project_structure,
    list_dirs,
    rename_files,
    rename_dirs
)
```

Now, let's create project folder hierarchy by running the following command. Assuming that you are located in your 


```
create_project_structure(base_path="./")
```

After that, you should see in your project something like that:

```
your_project/
├── datasets/
├── config/
├── outputs/
├── logs/
```

Move both datasets, training and validation, into your project’s `./datasets/` folder.

```bash
./datasets/BraTS2025_train/
./datasets/BraTS2025_val/
```

Define your datasets paths as follows:

```python
train_data_path = "./datasets/BraTS2025_train/"
val_data_path = "./datasets/BraTS2025_val/"
```

If everything is correct, you should see subfolders like:

```python
# Preview first subfolders
print(list_dirs(train_data_path)[:10])

['BraTS-GLI-00000-000', 'BraTS-GLI-00002-000', ...]
```


---

## 4. Standardize Folder and File Naming

To ensure compatibility with AUDIT, we will rename folders and files.

### 4.1 Rename Folders

We will replace the prefix `BraTS-GLI-` with dataset-specific names. Set the parameter *safe_mode* to True to avoid

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

### 4.2 Rename Files

The same applies to files:

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

### 4.3 Standardize Sequences

To make the sequence names clearer and consistent, we will replace suffixes:

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

---

## 5. Configure Feature Extraction

Now that the dataset is ready, let’s configure feature extraction. AUDIT requires a YAML configuration file with 
absolute paths. Create a file named `feature_extraction.yml` inside `configs/`:

```yaml
# Paths to all the datasets
data_paths:
  BraTS2025_train: '/home/usr/project/datasets/BraTS2025_train/'
  BraTS2025_val: '/home/usr/project/datasets/BraTS2025_val/'

# Sequences available
sequences:
  - '_t1'
  - '_t2'
  - '_t1ce'
  - '_flair'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# List of features to extract
features:
  statistical: true
  texture: true
  spatial: true
  tumor: true

# Output paths
output_path: '/home/usr/project/outputs/features'
logs_path: '/home/usr/project/logs/features'

# Resources
cpu_cores: 8
```

Run feature extraction with:

```bash
auditapp feature-extraction --config /home/usr/projects/configs/feature_extraction.yml
```

After execution, `/home/usr/project/outputs/features` will contain the extracted features for both training and 
validation datasets.

⚠️ **Important:** All paths must be absolute. Otherwise, AUDIT may fallback to its internal default config files.

---

## 6. Launch the Web App

Once features are extracted, we can explore them using the web app. Create a config file named `app.yml`:

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
  EDE: 3
  ENH: 1
  NEC: 2

# Root paths
datasets_path: '/home/usr/project/datasets'
features_path: '/home/usr/project/outputs/features'
metrics_path: '/home/usr/project/outputs/metrics'

# Raw datasets
raw_datasets:
  BraTS2025_train: "${datasets_path}/BraTS2025_train"
  BraTS2025_val: "${datasets_path}/BraTS2025_val"

# Feature extraction CSVs
features:
  BraTS2025_train: "${features_path}/extracted_information_BraTS2025_train.csv"
  BraTS2025_val: "${features_path}/extracted_information_BraTS2025_val.csv"

# Metric extraction CSVs
metrics:

# Model predictions
predictions:
```

Launch the app with:

```bash
auditapp run-app --config /home/usr/projects/configs/app.yml
```

---


### Best Practices

* Always use **absolute paths** in configs.
* Verify sequence naming before running extraction.
* Start with a clean environment to avoid dependency conflicts.

By following this guided workflow, you will be able to prepare BraTS 2025 datasets for feature extraction and 
visualization consistently.
