import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import argparse
from pathlib import Path

from audit.utils.internal._config_helpers import check_app_config
from audit.utils.internal._config_helpers import load_config_file


def run_streamlit_app(config):
    # Get the path to the APP.py file
    app_path = Path(__file__).resolve().parent / "APP.py"

    # Ensure the app exists
    if not app_path.exists():
        raise FileNotFoundError(f"Streamlit app not found at: {app_path}")

    # Build the command to launch Streamlit with the provided config
    command = f"streamlit run {app_path} --server.fileWatcherType none -- --config {config}"

    # Print and execute the command
    print(f"Running command: {command}")
    os.system(command)


def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="AUDIT web APP.")
    parser.add_argument(
        "--config",
        type=str,
        default="./configs/app.yml",  # Path relative to the script location
        help="Path to the configuration file for web app.",
    )
    args = parser.parse_args()

    config = load_config_file(args.config)
    check_app_config(config)

    run_streamlit_app(args.config)


if __name__ == "__main__":
    main()
