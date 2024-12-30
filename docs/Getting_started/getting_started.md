# Getting Started

Welcome to **AUDIT**! Follow these steps to install, configure, and use AUDIT for analyzing MRI datasets and evaluating AI models.

---

## 1. Installation


### 1.1 Using PIP
Install AUDIT directly from PyPI (when available): 

```bash
pip install AUDIT
```

This is the simplest method if you just want to use the library without modifying the source code.

---

### 1.2 Using AUDIT repository

For development or if you need access to the latest updates, install AUDIT from the repository:

1. **Create an isolated environment** (recommended for avoiding dependency conflicts):  
    
    ```bash
    conda create -n audit_env python=3.10
    conda activate audit_env
    ```

2. **Clone the repository**:  

    ```bash
    git clone https://github.com/caumente/AUDIT.git
    cd AUDIT
    ```

3. **Install the required dependencies**: 

    ```bash
    pip install -r requirements.txt
    ```

---

### 1.3 Using Poetry

Poetry is a dependency manager that simplifies library management and environment creation. Follow these steps:

1. **Ensure Poetry is installed** in your environment.

2. **Clone the repository**:  

```bash
git clone https://github.com/caumente/AUDIT.git
cd AUDIT
```

3. **Install the dependencies**:  

```bash
poetry install
```

4. **Activate the virtual environment**:  

```bash
poetry shell
```

---

## 2. Configuration

AUDIT uses configuration files to define paths, settings, and parameters. These files are located in 
the `./src/configs/` directory:

- **Feature extractor**: Configure MRI features and datasets in `feature_extractor_config.json`.
- **Metric extractor**: Define evaluation metrics and paths in `metric_extractor_config.json`.
- **App settings**: Customize web app options in `app_config.json`.

Make sure to adjust other paths and settings according to your environment.

### 2.1. Example of feature extractor config file

This configuration file is used to define the settings for feature extraction in the AUDIT library. Each key and its usage is explained below:

- `data_paths`: Specifies the paths to the directories containing MRI datasets. It is a dictionary where each key 
                represents a dataset name (e.g., BraTS, UCSF), and the value is the file path to the dataset folder.
- `labels`: Maps region names (e.g., tumor labels) to their numeric values. This mapping is used to identify regions in 
            segmentation maps. 
      - BKG: Background (non-tumor regions). 
      - EDE: Edema. 
      - ENH: Enhancing tumor. 
      - NEC: Necrotic tumor tissue.
- `features`: Lists the types of features to be extracted from the MRI datasets. Each key is a feature type, and its 
              value (true or false) enables or disables that feature. Key Options:
      - statistical: Extract basic statistical properties (e.g., mean, variance) of the MRI intensity values.
      - texture: Compute texture-based features (e.g., entropy, contrast).
      - spatial: Analyze spatial properties (e.g., brain location, spatial resolution).
      - tumor: Extract tumor-specific features (e.g., tumor volume, tumor location).
- `longitudinal`: Configures settings for longitudinal studies, allowing analysis of changes in subjects over time. Each 
                dataset can have a unique configuration.
      - pattern: A delimiter (e.g., _, -, or /) used to split filenames.
      - longitudinal_id: The position (0-based index) in the split filename where the subject ID is located.
      - time_point: The position (0-based index) in the split filename indicating the time point (e.g., pre-treatment, post-treatment).
- `output_path`: Specifies the directory where extracted features will be saved.

Below is a complete configuration file, demonstrating how these keys are used together:

```json
# Paths to all your datasets
data_paths:
  BraTS: '/home/user/AUDIT/datasets/BraTS/BraTS_images'
  UCSF: '/home/user/AUDIT/datasets/UCSF/UCSF_images'

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
  spatial: true
  tumor: true

# Longitudinal settings (if longitudinal data is available)
longitudinal:
  UCSF:
    pattern: "_"            # Pattern used for splitting filename
    longitudinal_id: 1      # Index position for the subject ID after splitting the filename
    time_point: 2           # Index position for the time point after splitting the filename


# Path where extracted features will be saved
output_path: '/home/user/AUDIT/outputs/features'
```

### 2.2. Example of metric extractor config file

This configuration file is used to define the settings for feature extraction in the AUDIT library. Each key and its 
usage is explained below:

- `data_paths`: Specifies the paths to the directories containing MRI datasets. It is a dictionary where each key 
                represents a dataset name (e.g., BraTS, UCSF), and the value is the file path to the dataset folder.
- `model_predictions_paths`: Specifies the paths to the directories containing model predictions. It is a dictionary where each key 
                represents a model name (e.g., nn-UNet, SegResNet), and the value is the corresponding path.
- `labels`: Maps region names (e.g., tumor labels) to their numeric values. This mapping is used to identify regions in 
            segmentation maps. 
      - BKG: Background (non-tumor regions). 
      - EDE: Edema. 
      - ENH: Enhancing tumor. 
      - NEC: Necrotic tumor tissue.
- `metrics`: Lists the metrics to be computed to evaluate the model predictions. Each key represents a metric, and its 
             value (true or false) enables or disables the computation of that metric. Available options include: dice,
             jacc, accu, prec, sens, spec, haus, size.
- `package`: Specifies the library used to compute the metrics. AUDIT will be used by default.
- `calculate_stats`: A flag that determines whether additional statistical information (e.g., mean, variance) is 
                     computed for the evaluation. Only available is using pymia library.
- `output_path`: Specifies the directory where the computed metrics will be saved after evaluation.
- `filename`: Defines the filename prefix for saving the output metrics.

Below is a complete configuration file, demonstrating how these keys are used together:

```json
# Path to the raw dataset
data_path: '/home/user/AUDIT/datasets/BraTS/BraTS_images'

# Paths to model predictions
model_predictions_paths:
  nnUnet: '/home/user/AUDIT/datasets/BraTS/BraTS_seg/nnUnet'

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
package: custom
calculate_stats: false

# Path where output metrics will be saved
output_path: '/home/user/AUDIT/outputs/metrics'

# Filename for the extracted information
filename: 'BraTS'
```


### 2.3. Example of APP web config file
This configuration file is used to define the settings for organizing datasets, feature extractions, and model 
predictions in the AUDIT library. Each key is explained below:

- `labels`: Maps region names (e.g., tumor labels) to their numeric values. This mapping is used to identify regions in 
            segmentation maps. 
      - BKG: Background (non-tumor regions). 
      - EDE: Edema. 
      - ENH: Enhancing tumor. 
      - NEC: Necrotic tumor tissue.
- `features_path`: Defines the root path where the feature extraction results are saved.
- `metrics_path`: Defines the root path where the metric extraction results are saved.
- `raw_datasets`: Specifies paths to directories containing the raw MRI datasets. Each key represents a dataset name 
                  (e.g., BraTS, UCSF), and the value is the file path to the respective dataset folder.
- `features`: Specifies paths to CSV files where the extracted feature information is saved for each dataset. Each key 
              represents a dataset name, and the value is the file path to the corresponding feature extraction CSV file.
- `metrics`: Specifies paths to CSV files where metric extraction information is saved for each dataset. Similar to the
             features section, each key represents a dataset name, and the value is the path to the corresponding metrics CSV file.
- `predictions`: Specifies the paths for model predictions for different datasets. Each dataset name 
                 (e.g., BraTS_SSA) maps to a dictionary containing model names (e.g., nnUnet, SegResNet) as keys, 
                 and the file paths to their respective segmentation predictions as values.

```json
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
  BraTS: "${datasets_path}/BraTS/BraTS_images"
  BraTS_SSA: "${datasets_path}/BraTS_SSA/BraTS_SSA_images"
  UCSF: "${datasets_path}/UCSF/UCSF_images"

# Paths for feature extraction CSV files
features:
  BraTS: "${features_path}/extracted_information_BraTS.csv"
  BraTS_SSA: "${features_path}/extracted_information_BraTS_SSA.csv"
  UCSF: "${features_path}/extracted_information_UCSF.csv"

# Paths for metric extraction CSV files
metrics:
  BraTS_SSA: "${metrics_path}/extracted_information_BraTS.csv"
  UCSF: "${metrics_path}/extracted_information_UCSF.csv"

# Paths for models predictions
predictions:
  BraTS_SSA:
    nnUnet: "${datasets_path}/BraTS_SSA/BraTS_SSA_seg/nnUnet"
    SegResNet: "${datasets_path}/BraTS_SSA/BraTS_SSA_seg/SegResNet"
  UCSF:
    SegResNet: "${datasets_path}/UCSF/UCSF_seg/SegResNet"
```


---

## 3. Run AUDIT Backend

The backend processes data for analysis and evaluation. Run the following commands:

1. Run the feature extractor and metric extractor modules: 

```bash
python src/feature_extractor.py
python src/metric_extractor.py
```

Logs and output files will be saved in the directories specified in the configuration files (default is the 
outputs folder).

---

## 4. Run AUDIT App

The AUDIT web app provides an interactive interface for exploring your data and visualizing metrics. Start the app with:

```bash
streamlit run src/app/APP.py
```

This will open the app in your default web browser  at <a href="http://localhost:8501/" class="external-link" target="_blank">http://localhost:8501/</a>. Use the dashboards to:

- Explore univariate and multivariate data distributions.
- Compare model performance across datasets.
- Analyze trends in longitudinal data.

---

## 5. Additional Tips
For ITK-Snap integration, ensure it is installed and configured correctly.
Use the logs folder to monitor execution details for debugging.

You're all set to start using AUDIT! Dive into your MRI data, evaluate AI models, and gain deeper insights with the help of AUDIT’s powerful tools. For further details, check out the other sections of the documentation.