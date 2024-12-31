import os
from pathlib import Path


def main():
    # Get the path to the APP.py file
    app_path = Path(__file__).resolve().parent / "APP.py"

    # Ensure the app exists
    if not app_path.exists():
        raise FileNotFoundError(f"Streamlit app not found at: {app_path}")

    # Run the Streamlit app
    os.system(f"streamlit run {app_path}")
