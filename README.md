
[//]: # (![alt text]&#40;https://github.com/caumente/AUDIT/blob/main/src/app/util/images/AUDIT_big.jpeg&#41;)
![alt text](https://github.com/caumente/AUDIT/blob/main/src/app/util/images/AUDIT_medium.jpeg)


<a href="https://github.com/caumente/AUDIT" title="Go to GitHub repo"><img src="https://img.shields.io/static/v1?label=caumente&message=AUDIT&color=e78ac3&logo=github" alt="caumente - AUDIT"></a>
<a href="https://github.com/caumente/AUDIT"><img src="https://img.shields.io/github/stars/caumente/AUDIT?style=social" alt="stars - AUDIT"></a>
<a href="https://github.com/caumente/AUDIT"><img src="https://img.shields.io/github/forks/caumente/AUDIT?style=social" alt="forks - AUDIT"></a>


<a href="https://github.com/caumente/audit/releases/"><img src="https://img.shields.io/github/release/caumente/audit?include_prereleases=&sort=semver&color=e78ac3" alt="GitHub release"></a>
<a href="#license"><img src="https://img.shields.io/badge/License-Apache_2.0-e78ac3" alt="License"></a>
<a href="https://github.com/caumente/audit/issues"><img src="https://img.shields.io/github/issues/caumente/audit" alt="issues - AUDIT"></a>


## Summary

AUDIT, Analysis & evalUation Dashboard of artIficial inTelligence, is a tool designed to analyze,
visualize, and detect biases in brain MRI data and models. It provides tools for loading and processing MRI data,
extracting relevant features, and visualizing model performance and biases in predictions. AUDIT presents the 
following features:


- **Data management**: Easily work with MRI data from various sources.
- **Feature extraction**: Extract relevant features from MRI images and their segmentations for analysis.
- **Visualization**: Visualize model performance, including false positives and negatives, using interactive plots.
- **Model robustness**: Assess the robustness of the model by evaluating its performance across different datasets and conditions.
- **Bias detection**: Identify potential biases in model predictions and performance.
- **Longitudinal analysis**: Track your model performance over different time points.

Details of our work are provided in [*our paper*](...........), **AUDIT**. We hope that 
users will use *AUDIT* to gain novel insights into brain tumor segmentation field. 


## Usage
- **Home Page**: The main landing page of the tool.
- **Univariate Analysis**: Analysis of individual variables to understand their distributions and characteristics.
- **Multivariate Analysis**: Examination of multiple variables simultaneously to explore relationships and patterns.
- **Segmentation Error Matrix**: A table displaying the errors associated with different segmentation tasks.
- **Model Performance Analysis**: Evaluation of the effectiveness and accuracy of a single model.
- **Pairwise Model Performance Comparison**: Comparison of performance metrics between two different models.
- **Multi-model Performance Comparison**: Comparative analysis of performance metrics across multiple models.
- **Longitudinal Measurements**: Analysis of data collected over time to observe trends and changes.
- **Subjects Exploration**: Detailed examination of individual subjects within the dataset.


## Web AUDIT

Last released version of **AUDIT** is hosted at https://audit.streamlitapp.com for an online overview of its functionalities.


## Getting Started

### 1.1 Installation via PIP installer (Not available yet)

```bash
pip install audit
```

### 1.2. Installation via AUDIT repository 

### 1.2.1. Using Anaconda
(Recommended) Create an isolated Anaconda environment:

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

### 1.2.2 Using Poetry

The library _poetry_ must be installed in your environment to follow this via of installation.

Clone the repository:
 ```bash
 git clone https://github.com/caumente/AUDIT.git
 cd AUDIT
```

Install the dependencies:
```bash
poetry install
```

Activate virtual environment:
```bash
poetry shell
```


### 2. Configuration

Edit the config files in `./src/configs/` directory to set up the paths for data loading and other configurations:


<details>
  <summary><strong>2.1. Feature extractor config</strong></summary>

```yaml
# Paths to all the datasets
data_paths:
  dataset_1: '/home/user/AUDIT/datasets/dataset_1/dataset_1_images'
  dataset_N: '/home/user/AUDIT/datasets/dataset_N/dataset_N_images'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# List of features to extract
features:
  statistical: true
  texture: false
  spatial: false
  tumor: false

# Longitudinal study settings
#longitudinal:
#  dataset_N:
#    pattern: "_"            # Pattern used for splitting filename
#    longitudinal_id: 1      # Index position for the subject ID after splitting the filename
#    time_point: 2           # Index position for the time point after splitting the filename


# Path where extracted features will be saved
output_path: '/home/user/AUDIT/outputs/features'
```
</details>


<details>
  <summary><strong>2.2. Metric extractor config</strong></summary>

```yaml
# Path to the raw dataset
data_path: '/home/carlos/AUDIT/datasets/dataset_1/dataset_1_images'

# Paths to model predictions
model_predictions_paths:
  model_1: '/home/user/AUDIT/datasets/dataset_1/dataset_1_seg/model_1'
  model_M: '/home/user/AUDIT/datasets/dataset_1/dataset_1_seg/model_M'

# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# List of metrics to compute
metrics:
  dice: true
  jacc: false
  accu: false
  prec: false
  sens: false
  spec: false
  haus: false

# Library used for computing all the metrics
package: custom
calculate_stats: false

# Path where output metrics will be saved
output_path: '/home/user/AUDIT/outputs/metrics'

# Filename for the extracted information
filename: 'dataset_1'
```
</details>


<details>
  <summary><strong>2.3. APP config</strong></summary>

```yaml
# Mapping of labels to their numeric values
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# Root path for datasets, features extracted, and metrics extracted
datasets_path: '/home/user/AUDIT/datasets'
features_path: '/home/user/AUDIT/outputs/features'
metrics_path: '/home/user/AUDIT/outputs/metrics'

# Paths for raw datasets
raw_datasets:
  dataset_1: "${datasets_path}/dataset_1/dataset_1_images"
  dataset_N: "${datasets_path}/dataset_N/dataset_N_images"

# Paths for feature extraction CSV files
features:
  dataset_1: "${features_path}/extracted_information_dataset_1.csv"
  dataset_N: "${features_path}/extracted_information_dataset_N.csv"

# Paths for metric extraction CSV files
metrics:
  dataset_1: "${metrics_path}/extracted_information_dataset_1.csv"
  dataset_N: "${metrics_path}/extracted_information_dataset_N.csv"

# Paths for models predictions
predictions:
  dataset_1:
    model_1: "${datasets_path}/dataset_1/dataset_1_seg/model_1"
    model_M: "${datasets_path}/dataset_1/dataset_1_seg/model_M"
  dataset_N:
    model_1: "${datasets_path}/dataset_N/dataset_N_seg/model_1"
    model_M: "${datasets_path}/dataset_N/dataset_N_seg/model_M"
```
</details>


### 3. Run AUDIT backend

Use the following commands to run the *Feature extractor* and *Metric extractor* scripts:

```bash
python src/feature_extractor.py
```

```bash
python src/metric_extractor.py
```

A _logs_ folder will be created after running each of the scripts to keep track of the execution. All the output files 
will be stored in the folder defined in the corresponding config file (by default in the _output_ folder).

### 4. Run AUDIT app

Use the following streamlit command to run the APP and start the data exploration:

```bash
streamlit run src/app/APP.py
```

### 5. Additional configurations

#### 5.1. ITK-Snap

AUDIT is prepared for opening cases with ITK-Snap while exploring the data in the different dashboards. However, the 
ITK-Snap tool must have been installed and preconfigured before. Here we provide a simple necessary configuration to 
use it in each operative system:

<details>
  <summary><strong>5.1.1. On Mac OS</strong></summary>

```bash
```
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





