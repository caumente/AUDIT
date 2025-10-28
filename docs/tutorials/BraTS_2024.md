# BraTS 2024 Tutorial

This tutorial will guide you step by step to prepare the BraTS 2024 dataset, organize it, configure feature extraction, 
and finally launch the web app to explore the data.

The BraTS 2024 dataset is special because it includes a mapping file containing demographic information.
For example, for each patient, it specifies the glioma type, the magnetic field strength used during MRI acquisition, sex, and other variables.
The goal of this tutorial is not only to analyze the cohort at a high level (as done in the BraTS 2025 tutorial) but 
also to dive deeper and identify potential biases or peculiarities that may go unnoticed when no specific analysis is performed.

AUDIT provides a broader perspective, helping understand differences within a dataset, analyze model performance 
based on demographic variables, and more.

---

## 1. Prerequisites

Before starting this tutorial, you should have reviewed the BraTS 2025 tutorial, as concepts and functionalities 
explained there are assumed here.

As in the previous tutorial, we recommend using an Anaconda environment with Jupyter Notebook, creating the project 
structure, and understanding how AUDIT configuration files work.

The BraTS 2025 dataset is hosted on Synapse and **requires prior registration**. Please follow the [official 
instructions](https://www.synapse.org/Synapse:syn64153130/wiki/) from the challenge and to BraTS 2025
[Data Access](https://www.synapse.org/Synapse:syn64377310) section to download the data. For this tutorial we will take
advantage of both datasets training and validation. 

Once downloaded and unzipped, store the training and additional training sets in a directory called `.datasets/BraTS_2024`.
The metadata file must be stored in the project root. The project structure should look like this before starting:

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

Before working with the images, we need to understand what information we have about the patients. The BraTS 2024 
dataset comes with a spreadsheet that contains demographics, glioma types, MRI scanner info, and more.
By looking at this data first, we can plan our analyses and later see if our model behaves differently across sites 
or patient characteristics.

Let's load this spreadsheet into a pandas DataFrame and take a first look:

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


Notice how each patient has a site, age, sex, and glioma type. Later, we can use this information to organize the 
dataset and check for potential biases.


For now, we will focus on analyzing the differences between cases from different acquisition sites. However, we 
encourage users to perform their own analyses, exploring stratifications by glioma type, magnetic field strength, manufacturer, and other variables.
The goal is to show how AUDIT can help you better understand your dataset and perform a more accurate evaluation of segmentation models and MRI cohorts.

For this tutorial, we will work only with the training and additional training cohorts, excluding the validation set.


```python
df = mapping[mapping["Train/Test/Validation "].isin(["Train", "Train-additional"])]
```

Let's create a function to move each patient into their corresponding folder, instead of keeping all of them grouped in a single directory.

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

This function allows you to organize patients into separate directories and can be reused for any other analysis you want to perform with the BraTS 2024 dataset.

```python
input_dir = "./datasets/BraTS_2024"
output_dir = "./datasets/BraTS_2024_by_site"

organize_patients(df, column="Site", input_dir=input_dir, output_dir=output_dir)
```

Ready! After running this, your project should have the following structure:

```
brats2024_project/
├── datasets/
├──── BraTS_2024/
├──── BraTS_2024_by_site/
├────── Duke/
├──────── BraTS-GLI-02060-100/
├──────── BraTS-GLI-02060-101/
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


## 3. Standardize folder and file naming

To ensure compatibility with AUDIT, we will rename folders and files. Check XXXX out for more details.


We will replace the prefix `BraTS-GLI-` with dataset-specific names. Set the parameter *safe_mode* to True to avoid

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


Finally, for consistency, we replace all `-` characters with `_`:

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
  Duke: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Duke/'
  Indiana: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Indiana/'
  Missouri: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/Missouri/'
  UCSD: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/UCSD/'
  UCSF: '/home/usr/brats2024_project/datasets/BraTS_2024_by_site/UCSF/'

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

⚠️ **Important:** All paths must be absolute. Otherwise, AUDIT may fallback to its internal default config files.

---

## 6. Launch the dashboard

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
  EDE: 3
  ENH: 1
  NEC: 2

# Root paths
datasets_path: '/home/c062o/Documents/example/brats2024_project/datasets/BraTS_2024_by_site'
features_path: '/home/c062o/Documents/example/brats2024_project/outputs/features'
metrics_path: '/home/c062o/Documents/example/brats2024_project/outputs/metrics'

# Raw datasets
raw_datasets:
  Duke: "${datasets_path}/Duke"
  Indiana: "${datasets_path}/Indiana"
  Missouri: "${datasets_path}/Missouri"
  UCSD: "${datasets_path}/UCSD"
  UCSF: "${datasets_path}/UCSF"

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





---


