# Installation Guide

Welcome to AUDIT! Before installing on your local computer, we recommend exploring the publicly deployed app on Streamlit Cloud:

[https://auditapp.streamlit.app/](https://auditapp.streamlit.app/)

This allows you to try AUDIT without any setup. When you're ready to analyze your own datasets or use advanced features, follow the steps below to install AUDIT locally.

---

## 🏆 Installation via Repository (Recommended)

For full flexibility, access to the latest updates, and example files, we recommend installing AUDIT by cloning the official repository. This method is suitable for most users, including those who want to customize or contribute to the project.

Choose one of the following options:

### Option 1: Using Conda

1. **Create an isolated environment** (recommended to avoid dependency conflicts):
    
    ```bash
    conda create -n audit_env python=3.10
    conda activate audit_env
    ```

2. **Clone the repository**:
    
    ```bash
    git clone https://github.com/caumente/AUDIT.git
    cd AUDIT
    ```

3. **Install dependencies**:
    
    ```bash
    pip install -r requirements.txt
    ```

---

### Option 2: Using Poetry

Poetry is a modern dependency manager that simplifies library management and environment creation.

1. **Install Poetry** (if not already installed):
    
    [Poetry installation guide](https://python-poetry.org/docs/#installation)

2. **Clone the repository**:
    
    ```bash
    git clone https://github.com/caumente/AUDIT.git
    cd AUDIT
    ```

3. **Install dependencies**:
    
    ```bash
    poetry install
    ```

4. **Activate the virtual environment**:
    
    ```bash
    poetry shell
    ```

---

## 📦 Installation via PyPI

If you want a quick way to use AUDIT for data analysis and evaluation, you can install the latest stable version from PyPI:

```bash
pip install auditapp
```

This method is ideal for users who do not need to modify the source code. You will still need to set up configuration files and the recommended project structure.

!!! tip
    If you encounter issues with permissions, try running `pip install --user auditapp`.

---

## ✅ What’s Next?

- The repository installation provides greater flexibility and access to example cases, project structure templates, and outputs.
- Example configuration files and datasets are included in the repository to help you get started quickly.
- For details on project structure, configuration, and running AUDIT, see the other sections in the documentation.

!!! info
    The recommended workflow is to install AUDIT via the repository for full functionality and easier customization.

---

## 🧩 Troubleshooting & Tips

- If you have issues with Python versions, ensure you are using Python 3.10 or higher.
- For help with dependencies, check the requirements.txt or pyproject.toml files.
- For more information, visit the [AUDIT GitHub repository](https://github.com/caumente/AUDIT).

You're ready to start using AUDIT! For further guidance, explore the rest of the documentation.
