import re
from pathlib import Path

import yaml


def load_config_file(path: str) -> dict:
    """
    Loads a configuration file in YAML format and returns its contents as a dictionary.

    Args:
        path: The relative file root_dir to the YAML configuration file.

    Returns:
        dict: The contents of the YAML file as a dictionary.
    """

    def replace_variables(config, variables):
        def replace(match):
            return variables.get(match.group(1), match.group(0))

        for key, value in config.items():
            if isinstance(value, str):
                config[key] = re.sub(r"\$\{(\w+)\}", replace, value)
            elif isinstance(value, dict):
                replace_variables(value, variables)

    # Resolve the absolute root_dir based on the current file's path
    base_dir = Path(__file__).resolve().parent.parent.parent  # Adjust the depth according to your project
    absolute_path = base_dir / path

    # Validate if the file exists
    if not absolute_path.exists():
        raise FileNotFoundError(f"Config file not found: {absolute_path}")

    # Load the YAML file
    with open(absolute_path, "r") as file:
        config = yaml.safe_load(file)

    # Replace variables in the YAML configuration
    variables = {key: value for key, value in config.items() if not isinstance(value, dict)}
    replace_variables(config, variables)

    return config
