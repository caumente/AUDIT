
![alt text](https://github.com/caumente/AUDIT/blob/main/src/audit/app/util/images/AUDIT_medium.jpeg)


<a href="https://github.com/caumente/AUDIT" title="Go to GitHub repo"><img src="https://img.shields.io/static/v1?label=caumente&message=AUDIT&color=e78ac3&logo=github" alt="caumente - AUDIT"></a>
<a href="https://github.com/caumente/AUDIT"><img src="https://img.shields.io/github/stars/caumente/AUDIT?style=social" alt="stars - AUDIT"></a>
<a href="https://github.com/caumente/AUDIT"><img src="https://img.shields.io/github/forks/caumente/AUDIT?style=social" alt="forks - AUDIT"></a>


<a href="https://github.com/caumente/audit/releases/"><img src="https://img.shields.io/github/release/caumente/audit?include_prereleases=&sort=semver&color=e78ac3" alt="GitHub release"></a>
<a href="#license"><img src="https://img.shields.io/badge/License-Apache_2.0-e78ac3" alt="License"></a>
<a href="https://github.com/caumente/audit/issues"><img src="https://img.shields.io/github/issues/caumente/audit" alt="issues - AUDIT"></a>


## Summary

AUDIT, Analysis & evalUation Dashboard of artIficial inTelligence, is a tool designed to provide
researchers and developers an interactive way to better analyze and explore MRI datasets and segmentation models.
Given its functionalities to extract the most relevant features and metrics from your several data sources, it
allows for uncovering biases both intra and inter-dataset as well as within the model predictions. Some of the main
capabilities of AUDIT are presented below:

- **Data management**: Easily work and preprocess MRIs from various sources.
- **Feature extraction**: Extract relevant features from the images and their segmentations for analysis.
- **Model robustness**: Assess model generalization by evaluating its performance across several experiments
                        and conditions.
- **Bias detection**: Identify potential biases either in model predictions and performance or on your data.
- **Longitudinal analysis**: Track the model performance over different time points.
- **High compatibility**: Provides connection with tools like ITK-SNAP and other external tools.

Details of our work are provided in our paper [*AUDIT: An open-source Python library for AI model evaluation with use cases in MRI brain tumor segmentation*](https://doi.org/10.1016/j.cmpb.2025.108991), **AUDIT**. We hope that users will use *AUDIT* to gain novel insights into medical image segmentation field.

## Usage

- **Home Page**: The main landing page of the tool.
- **Univariate Analysis**: Exploration of individual variables to understand their distributions and discover
                           outliers in it.
- **Multivariate Analysis**: Examination of multiple variables simultaneously to explore relationships and
                             hidden patterns.
- **Segmentation Error Matrix**: A pseudo-confusion matrix displaying the errors associated with the
                                 segmentation tasks.
- **Model Performance Analysis**: Evaluation of the effectiveness and accuracy of a single model.
- **Pairwise Model Performance Comparison**: Perform pair-wise comparisons between models to find statistical
                                             significant differences.
- **Multi-model Performance Comparison**: Comparative analysis of performance metrics across multiple models.
- **Longitudinal Measurements**: Analysis of data collected over time to observe trends and changes on model
                                 accuracy.
- **Subjects Exploration**: Detailed examination of individual subjects within the dataset.

## Web app

Last released version of **AUDIT** is hosted at https://auditapp.streamlitapp.com for an online overview of its functionalities.

## Getting Started

AUDIT library can be installed either from our repository or PYPI repository through the command _pip install auditapp_. 
Here we will show how to do it following the first approach. For a more detailed exploration of AUDIT, please check our 
[*official documentation*](https://github.com/caumente/AUDIT).

### 1 Installation 

Create an isolated Anaconda environment:

```bash
conda create -n audit_env python=3.10
conda activate audit_env
```

Clone the repository:
 ```bash
 git clone https://github.com/caumente/AUDIT.git
 cd AUDIT
 ```

Install the required packages:
 ```bash
 pip install -r requirements.txt
 ```

### 2. Configuration

Edit the config files in `./src/audit/configs/` directory to set up the paths for data loading and other configurations:


<details>
  <summary><strong>2.1. Feature extraction config file</strong></summary>

```yaml
# Paths to all the datasets
data_paths:
  BraTS2020: '/home/usr/AUDIT/datasets/BraTS2020/BraTS2020_images'
  BraTS2024_PED: '/home/usr/AUDIT/datasets/BraTS2024_PED/BraTS2024_PED_images'
  BraTS2024_SSA: '/home/usr/AUDIT/datasets/BraTS2024_SSA/BraTS2024_SSA_images'
  UCSF: '/home/usr/AUDIT/datasets/UCSF/UCSF_images'
  LUMIERE: '/home/usr/AUDIT/datasets/LUMIERE/LUMIERE_images'

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

# Longitudinal study settings
longitudinal:
  UCSF:
    pattern: "_"            # Pattern used for splitting filename
    longitudinal_id: 1      # Index position for the subject ID after splitting the filename. Starting by 0
    time_point: 2           # Index position for the time point after splitting the filename. Starting by 0
  LUMIERE:
    pattern: "-"
    longitudinal_id: 1
    time_point: 3

# Path where extracted features will be saved
output_path: '/home/usr/AUDIT/outputs/features'
logs_path: '/home/usr/AUDIT/logs/features'

# others
cpu_cores: 8
```
</details>


<details>
  <summary><strong>2.2. Metric extraction config file</strong></summary>

```yaml
# Path to the raw dataset
data_path: '/home/usr/AUDIT/datasets/BraTS2024_PED/BraTS2024_PED_images'

# Paths to model predictions
model_predictions_paths:
  nnUnet: '/home/usr/AUDIT/datasets/BraTS2024_PED/BraTS2024_PED_seg/nnUnet'
  SegResNet: '/home/usr/AUDIT/datasets/BraTS2024_PED/BraTS2024_PED_seg/SegResNet'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

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
output_path: '/home/usr/AUDIT/outputs/metrics'
filename: 'BraTS2024_PED'
logs_path: '/home/usr/AUDIT/logs/metric'

# others
cpu_cores: 8
```
</details>


<details>
  <summary><strong>2.3. APP config file</strong></summary>

```yaml
# Sequences available. First of them will be used to compute properties like spacing
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

# Root path for datasets, features extracted, and metrics extracted
datasets_path: './datasets'  # '/home/usr/AUDIT/datasets'
features_path: './outputs/features'  # '/home/usr/AUDIT/outputs/features'
metrics_path: './outputs/metrics'  # '/home/usr/AUDIT/outputs/metrics'

# Paths for raw datasets
raw_datasets:
  BraTS2020: "${datasets_path}/BraTS2020/BraTS2020_images"
  BraTS2024_SSA: "${datasets_path}/BraTS2024_SSA/BraTS2024_SSA_images"
  BraTS2024_PED: "${datasets_path}/BraTS2024_PED/BraTS2024_PED_images"
  UCSF: "${datasets_path}/UCSF/UCSF_images"
  LUMIERE: "${datasets_path}/LUMIERE/LUMIERE_images"

# Paths for feature extraction CSV files
features:
  BraTS2020: "${features_path}/extracted_information_BraTS2020.csv"
  BraTS2024_SSA: "${features_path}/extracted_information_BraTS2024_SSA.csv"
  BraTS2024_PED: "${features_path}/extracted_information_BraTS2024_PED.csv"
  UCSF: "${features_path}/extracted_information_UCSF.csv"
  LUMIERE: "${features_path}/extracted_information_LUMIERE.csv"

# Paths for metric extraction CSV files
metrics:
  BraTS2024_SSA: "${metrics_path}/extracted_information_BraTS2024_SSA.csv"
  BraTS2024_PED: "${metrics_path}/extracted_information_BraTS2024_PED.csv"
  UCSF: "${metrics_path}/extracted_information_UCSF.csv"
  LUMIERE: "${metrics_path}/extracted_information_LUMIERE.csv"

# Paths for models predictions
predictions:
  BraTS2024_SSA:
    nnUnet: "${datasets_path}/BraTS2024_SSA/BraTS2024_SSA_seg/nnUnet"
    SegResNet: "${datasets_path}/BraTS2024_SSA/BraTS2024_SSA_seg/SegResNet"
  BraTS2024_PED:
    nnUnet: "${datasets_path}/BraTS2024_PED/BraTS2024_PED_seg/nnUnet"
    SegResNet: "${datasets_path}/BraTS2024_PED/BraTS2024_PED_seg/SegResNet"
```
</details>

### 3. Run AUDIT backend

Use the following commands to run the *Feature extraction* and *Metric extraction* scripts from your terminal:

```bash
python src/audit/feature_extraction.py
```

```bash
python src/audit/metric_extraction.py
```

A _logs_ folder will be created after running each of the scripts to keep track of the execution. All the output files 
will be stored in the folder defined in the corresponding config file (by default in the _outputs_ folder).

### 4. Run AUDIT app

AUDIT app is build on top of Streamlit library. Use the following command to run the APP and start the data exploration:

```bash
python src/audit/app/launcher.py
```

### 5. Additional configurations

#### 5.1. ITK-Snap

AUDIT can be adjusted for opening cases with ITK-Snap while exploring the data in the different dashboards. The 
ITK-Snap tool must have been installed and preconfigured before. Here we provide a simple necessary configuration to 
use it in each operative system:

<details>
  <summary><strong>5.1.1. On Mac OS</strong></summary>


</details>


<details>
  <summary><strong>5.1.2. On Linux OS</strong></summary>

```bash
```
</details>


## Authors

Please feel free to contact us with any issues, comments, or questions.

#### Carlos Aumente 

- Email: <UO297103@uniovi.es>
- GitHub: https://github.com/caumente

#### Mauricio Reyes 
#### Michael Muller 
#### Jorge Díez 
#### Beatriz Remeseiro 

## License
Apache License 2.0




