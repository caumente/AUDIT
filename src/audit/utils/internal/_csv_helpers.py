import os

import pandas as pd


def concatenate_csv_files(path: str, output_file: str):
    """
    Concatenates all CSV files in a specified directory into a single CSV file.

    Args:
        path: The directory containing the CSV files to concatenate.
        output_file: The root_dir where the concatenated CSV file will be saved.
    """
    csv_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".csv")]
    df_list = [pd.read_csv(csv_file) for csv_file in csv_files]
    concatenated_df = pd.concat(df_list, ignore_index=True)
    concatenated_df.to_csv(output_file, index=False)
    print(f"Concatenated CSV files saved to: {output_file}")


def read_datasets_from_dict(name_path_dict: dict, col_name: str = "set") -> pd.DataFrame:
    """
    Reads multiple datasets from a dictionary of name-root_dir pairs and concatenates them into a single DataFrame.

    Args:
        name_path_dict: A dictionary where keys are dataset names and values are file paths to CSV files.
        col_name: The name of the column to add that will contain the dataset name. Defaults to "set".

    Returns:
        pd.DataFrame: A concatenated DataFrame containing all the datasets, with an additional column specifying
                      the dataset name.
    """

    out = []
    for name, path in name_path_dict.items():
        data = pd.read_csv(path)
        data[col_name] = name
        out.append(data)
    out = pd.concat(out)

    return out
