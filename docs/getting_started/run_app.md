# Running AUDIT Web App

AUDIT provides an interactive web app for data exploration and visualization. We recommend running the app from the cloned repository for full access to features and customization.

---

## ▶️ Run from Repository (Recommended)

Start the app using:

```bash
python src/audit/app/launcher.py --config path/to/your/app.yaml
```

!!! info
    The `--config` parameter is optional if you edit the default configuration file in `src/audit/configs/app.yaml`.

---

## ▶️ Run from PyPI Installation

If installed via PyPI, use:

```bash
auditapp run-app --config path/to/your/app.yaml
```

---

## 🌐 Accessing the App

- The app will open in your default web browser at [http://localhost:8501/](http://localhost:8501/).
- Use the dashboards to explore data distributions, compare model performance, and analyze trends.

---

## 🏁 Getting Started

- Example configuration files are available in the repository.
- For more details, see the configuration and project structure guides.

!!! tip
    For full functionality, use the repository installation and default configuration files.
