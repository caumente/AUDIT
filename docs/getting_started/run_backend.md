# Running AUDIT Backend

AUDIT's backend is responsible for extracting features from medical images and evaluating segmentation model performance using metrics. These steps are essential for understanding your data, benchmarking models, and generating results for further analysis and visualization.

Feature extraction computes quantitative descriptors (statistical, texture, spatial, tumor features) from your datasets, enabling detailed cohort analysis and model comparison. Metric extraction evaluates segmentation predictions against ground truth, providing objective measures of model accuracy and reliability.

All extraction and evaluation methods are documented in the [API reference](../API_reference/features/index.md).

---

## ▶️ Run from Repository (Recommended)

Use the following commands to run feature extraction and metric evaluation modules:

```bash
python src/audit/feature_extraction.py --config path/to/your/feature_extraction.yaml
python src/audit/metric_extraction.py --config path/to/your/metric_extraction.yaml
```

!!! info
    The `--config` parameter is optional if you edit the default configuration files in `src/audit/configs/`.

---

## ▶️ Run from PyPI Installation

If installed via PyPI, use the command-line interface:

```bash
auditapp feature-extraction --config full/path/to/your/feature_extraction.yaml
auditapp metric-extraction --config full/path/to/your/metric_extraction.yaml
```

Full path to your config files is mandatory. Otherwise, AUDIT might look for internal config files contained in the
library by default.

---

## 🏁 Getting Started

- Output and log files are saved in the directories specified in your configuration files.
- Example configuration files are available in the repository.
- For more details, see the configuration and project structure guides.
- For technical details, see the API reference documentation.

!!! tip
    For best results, use the repository installation and default configuration files.
