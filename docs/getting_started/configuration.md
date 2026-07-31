# Configuration guide

AUDIT uses YAML configuration files for feature extraction, metric evaluation,
and the app. The files live in `src/audit/configs/`.

Every workflow separates the clinical modality from the file format:

```yaml
modality: MRI
formats:
  image: .nii.gz
  segmentation: .nii.gz
  prediction: .nii.gz
```

`modality` selects domain behaviour. `formats` selects the storage reader.
See [Image formats and readers](image_formats.md) for all supported values and
reader options.

## Feature extraction

```yaml
data_paths:
  BraTS: /data/BraTS/images

modality: MRI
formats:
  image: .nii.gz
  segmentation: .nii.gz

sequences:
  - _t1
  - _t2
  - _t1ce
  - _flair

labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

features:
  statistical: true
  texture: true
  spatial: true
  tumor: true

preprocessing: {}

output_path: ./outputs/features
logs_path: ./logs/features
cpu_cores: 8
```

MRI requires an explicit sequence list. A single-image US dataset normally
uses `sequences: []`, `modality: US`, and a raster or DICOM format.

`preprocessing` is passed to the selected modality before feature extraction.
For example, US currently supports optional min-max normalization:

```yaml
preprocessing:
  normalize: true
```

## Metric extraction

```yaml
data_path: /data/BraTS/images

modality: MRI
formats:
  segmentation: .nii.gz
  prediction: .nii.gz

model_predictions_paths:
  nnUNet: /data/BraTS/predictions/nnUNet

labels:
  BKG: 0
  EDE: 3
  ENH: 1
  NEC: 2

backend: audit

metrics:
  dice: true
  jaccard: true
  accuracy: true
  precision: true
  sensitivity: true
  specificity: true
  hausdorff_distance: true
  predicted_size: true

output_path: ./outputs/metrics
filename: BraTS
logs_path: ./logs/metric
cpu_cores: 8
```

The metric names above are the canonical keys for `backend: audit`. pymia and
Metrics Reloaded expose their own documented metric keys so their additional
capabilities remain available. Consult the metric availability table before
switching backends.

## App

```yaml
modality: US
formats:
  image: .png
  segmentation: .png
  prediction: .png
sequences: []

labels:
  BKG: 0
  TUMOR: 255

datasets_path: ./datasets/US
features_path: ./outputs/features
metrics_path: ./outputs/metrics

raw_datasets:
  BUSI: "${datasets_path}/BUSI/images"

features:
  BUSI: "${features_path}/extracted_information_BUSI.csv"

metrics:
  BUSI: "${metrics_path}/extracted_information_BUSI.csv"

predictions:
  BUSI:
    nnUNet: "${datasets_path}/BUSI/predictions/nnUNet"
```

The app currently uses one global modality, format mapping, and label map.
Mixed MRI/US datasets and dataset-specific labels are not supported in one
execution.

!!! tip
    Keep experimental dataset paths in a separate example or local YAML file.
    The general configuration should describe the reusable workflow rather
    than a particular experiment.
