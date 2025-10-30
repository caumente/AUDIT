# Configuration Guide

AUDIT uses configuration files to define paths, settings, and parameters for feature extraction, metric evaluation, and 
app customization. We recommend starting from the example files included in the repository and adapting them to your 
needs.

---

## Configuration files

- **Feature extraction**: _feature_extraction.yaml_
- **Metric evaluation**: _metric_extraction.yaml_
- **App settings**: _app.yaml_

All configuration files are stored in the _config/_ directory.

---

## Example: Feature Extraction Config

Defines dataset paths, label mappings, features to extract, and longitudinal study settings.

```yaml
# Paths to datasets
data_paths:
  BraTS: '/home/user/AUDIT/datasets/BraTS/BraTS_images'
  UCSF: '/home/user/AUDIT/datasets/UCSF/UCSF_images'

# Label mapping
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# Features to extract
features:
  statistical: true
  texture: false
  spatial: true
  tumor: true

# Longitudinal settings
longitudinal:
  UCSF:
    pattern: "_"
    longitudinal_id: 1
    time_point: 2

# Output path
output_path: '/home/user/AUDIT/outputs/features'
```

---

## Example: Metric Extraction Config

Defines dataset and prediction paths, label mappings, metrics to compute, and output settings.

```yaml
# Dataset path
data_path: '/home/user/AUDIT/datasets/BraTS/BraTS_images'

# Model predictions
model_predictions_paths:
  nnUnet: '/home/user/AUDIT/datasets/BraTS/BraTS_seg/nnUnet'

# Label mapping
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

# Metrics to compute
metrics:
  dice: true
  jacc: true
  accu: true
  prec: true
  sens: true
  spec: true
  haus: true
  size: true

# Library and output
package: custom
calculate_stats: false
output_path: '/home/user/AUDIT/outputs/metrics'
filename: 'BraTS'
```

---

## Example: App Config

Defines dataset, feature, and metric paths for the web app.

```yaml
labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

datasets_path: '/home/user/AUDIT/datasets'
features_path: '/home/user/AUDIT/outputs/features'
metrics_path: '/home/user/AUDIT/outputs/metrics'

raw_datasets:
  BraTS: "${datasets_path}/BraTS/BraTS_images"
  UCSF: "${datasets_path}/UCSF/UCSF_images"

features:
  BraTS: "${features_path}/extracted_information_BraTS.csv"
  UCSF: "${features_path}/extracted_information_UCSF.csv"

metrics:
  UCSF: "${metrics_path}/extracted_information_UCSF.csv"

predictions:
  UCSF:
    SegResNet: "${datasets_path}/UCSF/UCSF_seg/SegResNet"
```

---

## Getting Started

- Start from the example configuration files in the repository.
- Adjust paths and settings to match your environment and project needs.
- For more details, see the API reference and other documentation sections.

!!! tip
    Consistent configuration ensures reproducible and reliable results.
