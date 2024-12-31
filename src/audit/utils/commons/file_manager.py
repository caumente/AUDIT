import os
import re
import shutil
from typing import Any

import pandas as pd
import yaml


def list_dirs(path: str) -> list:
    """
    Lists all directories within a given path and returns their names in sorted order.

    Args:
        path: The directory path where to look for subdirectories.

    Returns:
        list: A sorted list of directory names found within the specified path.
    """
    try:
        return sorted([f.path.split("/")[-1] for f in os.scandir(path) if f.is_dir()])
    except FileNotFoundError:
        print(f"Error: The path '{path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
        return []


def list_files(path: str) -> list:
    """
    Lists all files within a given path and returns their names in sorted order.

    Args:
        path: The directory path where to look for files.

    Returns:
        list: A sorted list of files names found within the specified path.
    """
    try:
        return sorted([f.path.split("/")[-1] for f in os.scandir(path) if f.is_file()])
    except FileNotFoundError:
        print(f"Error: The path '{path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
        return []


def load_config_file(path: str) -> dict:
    """
    Loads a configuration file in YAML format and returns its contents as a dictionary.

    Args:
        path: The file path to the YAML configuration file.

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

    with open(path, "r") as file:
        config = yaml.safe_load(file)

    variables = {key: value for key, value in config.items() if not isinstance(value, dict)}
    replace_variables(config, variables)

    return config


def rename_directories(path: str, old_name: str, new_name: str, verbose: bool = False, safe_mode: bool = True):
    """
    Renames all directories and subdirectories within a directory,
    replacing string_1 with string_2 in their names.

    Args:
        path (str): Path to the directory where renaming will be performed.
        old_name (str): The string to be replaced in the directory names.
        new_name (str): The new string that will replace string_1.
        verbose (bool): Whether to print verbose output for each rename operation.
        safe_mode (bool): If True, only simulates renaming without making changes.
    """

    if not os.path.exists(path):
        raise ValueError(f"The specified path {path} does not exist.")

    # Traverse the directory tree, renaming directories from the bottom up
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            if old_name in dir_name:
                new_dir_name = dir_name.replace(old_name, new_name)
                old_dir_path = os.path.join(root, dir_name)
                new_dir_path = os.path.join(root, new_dir_name)

                if safe_mode:
                    print(f"Would rename: {old_dir_path} -> {new_dir_path}")
                else:
                    try:
                        os.rename(old_dir_path, new_dir_path)
                        if verbose:
                            print(f"Directory renamed: {old_dir_path} -> {new_dir_path}")
                    except Exception as e:
                        print(f"Failed to rename {old_dir_path}: {e}")

    if safe_mode:
        print(f"Set dry_run parameter to False to rename the directories")


def add_string_directories(path: str, prefix: str = "", suffix: str = "", verbose: bool = False, safe_mode: bool = True):
    """
    Adds a prefix and/or suffix to all directories and subdirectories within a directory.

    Args:
        path (str): Path to the directory where renaming will be performed.
        prefix (str): The prefix to be added to the directory names.
        suffix (str): The suffix to be added to the directory names.
        verbose (bool): Whether to print verbose output for each rename operation.
        safe_mode (bool): If True, only simulates renaming without making changes.
    """
    # Traverse the directory tree, renaming directories from the bottom up
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            new_dir_name = f"{prefix}{dir_name}{suffix}"
            old_dir_path = os.path.join(root, dir_name)
            new_dir_path = os.path.join(root, new_dir_name)

            if new_dir_name != dir_name:  # Avoid renaming if no changes
                if safe_mode:
                    print(f"Would rename: {old_dir_path} -> {new_dir_path}")
                else:
                    try:
                        os.rename(old_dir_path, new_dir_path)
                        if verbose:
                            print(f"Directory renamed: {old_dir_path} -> {new_dir_path}")
                    except Exception as e:
                        print(f"Error renaming {old_dir_path} to {new_dir_path}: {e}")

    if safe_mode:
        print(f"Set safe_mode parameter to False to rename the directories")


def rename_files(path: str, old_name: str = "_t1ce", new_name: str = "_t1c", verbose: bool = False, safe_mode: bool = True):
    """
    Renames files in a directory and its subdirectories by replacing a specific substring in the filenames.

    This function recursively walks through all files in a specified root directory and its subdirectories,
    identifies files containing a specified old extension substring, and renames them by replacing
    the old extension with a new one.

    Args:
        path: The root directory containing the files to be renamed.
        old_name: The substring in filenames that needs to be replaced. Defaults to "_t1ce".
        new_name: The substring that will replace the old extension. Defaults to "_t1c".
        verbose: Whether print the log
        safe_mode: If True, the function will only simulate renaming without making any actual changes.
    """
    if old_name is None:
        old_name = ""

    if new_name is None:
        new_name = ""

    for subdir, _, files in os.walk(path):
        for file in files:
            # Check if the file contains the old_name
            if old_name in file:
                old_file_path = os.path.join(subdir, file)
                new_file_path = os.path.join(subdir, file.replace(old_name, new_name))

                if safe_mode:
                    # In safe mode, just print the potential renaming
                    print(f"[SAFE MODE] Would rename: {old_file_path} -> {new_file_path}")
                else:
                    try:
                        os.rename(old_file_path, new_file_path)

                        if verbose:
                            print(f"Renamed: {old_file_path} -> {new_file_path}")
                    except Exception as e:
                        print(f"Error renaming {old_file_path}: {e}")

    if safe_mode:
        print(f"Set safe_mode parameter to False to rename the files")


def copy_files_by_extension(
        src_dir: str,
        dst_dir: str,
        ext: str,
        safe_mode: bool = True,
        overwrite: bool = False,
        verbose: bool = False
):
    """
    Copies all files with a specific extension from one directory to another.

    Args:
        src_dir (str): The source directory from which to copy files.
        dst_dir (str): The destination directory where files will be copied.
        ext (str): The file extension to search for and copy (e.g., ".txt", ".yaml").
        safe_mode (bool): If True, simulates the operation without making changes.
        overwrite (bool): If True, allows overwriting existing files in the destination directory.
        verbose (bool): If True, prints detailed logs for each file operation.
    """

    if not os.path.exists(src_dir):
        raise ValueError(f"Source directory '{src_dir}' does not exist.")

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)  # Ensure destination directory exists

    copied_files = 0  # To keep track of how many files have been copied
    for subdir, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(ext):
                src_file_path = os.path.join(subdir, file)
                dst_file_path = os.path.join(dst_dir, file)

                # Check if the file already exists in the destination directory
                if not overwrite and os.path.exists(dst_file_path):
                    if verbose:
                        print(f"Skipped (exists): {src_file_path} -> {dst_file_path}")
                    continue  # Skip file if it exists and overwrite is False

                if safe_mode:
                    print(f"[SAFE MODE] Would copy: {src_file_path} -> {dst_file_path}")
                else:
                    try:
                        shutil.copy2(src_file_path, dst_file_path)  # Use copy2 to preserve metadata
                        copied_files += 1

                        if verbose:
                            print(f"Copied: {src_file_path} -> {dst_file_path}")
                    except Exception as e:
                        print(f"Error copying {src_file_path} to {dst_file_path}: {e}")

            # After all operations, report if any files were copied
            if copied_files == 0 and verbose:
                print(f"No files with the extension '{ext}' were found to copy.")
            elif verbose:
                print(f"Total files copied: {copied_files}")
                shutil.copy2(src_file_path, dst_file_path)
                print(f"Copied: {src_file_path} -> {dst_file_path}")


def delete_files_by_extension(root_dir: str, ext: str, verbose=False, safe_mode: bool = True):
    """
    Deletes all files with a specific extension in a directory and its subdirectories.

    Args:
        root_dir (str): The root directory where the search will start.
        ext (str): The file extension of the files to be deleted.
        safe_mode (bool): If True, simulates the deletion without actually removing the files.
        verbose (bool): If True, prints detailed logs for each file deletion operation.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"Root directory '{root_dir}' does not exist.")

    deleted_files = 0  # To keep track of how many files have been deleted

    # Walk through the directory tree
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(ext):
                file_path = os.path.join(subdir, file)

                if safe_mode:
                    # In safe mode, only print what would happen
                    print(f"[SAFE MODE] Would delete: {file_path}")
                else:
                    try:
                        os.remove(file_path)  # Delete the file
                        deleted_files += 1

                        if verbose:
                            print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

    # After all operations, report how many files were deleted
    if deleted_files == 0 and verbose:
        print(f"No files with the extension '{ext}' were found to delete.")
    elif verbose:
        print(f"Total files deleted: {deleted_files}")


def organize_files_into_folders(folder_path, extension='.nii.gz', verbose=False, safe_mode: bool = True):
    """
    Organizes files into folders based on their filenames. Each file will be moved into a folder named
    after the file (excluding the extension).

    Args:
        folder_path (str): Path to the folder containing the files.
        extension (str): The file extension to look for (default is '.nii.gz').
        safe_mode (bool): If True, simulates the file organization without moving the files.
        verbose (bool): If True, prints detailed logs about each file being organized.
    """

    if not os.path.exists(folder_path):
        raise ValueError(f"The directory '{folder_path}' does not exist.")

    # List all files in the given folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    organized_files = 0  # Counter to keep track of how many files were organized

    for file in files:
        # Extract the file name without extension
        file_name = file.split(extension)[0]

        # Create a new folder for the file
        folder_name = os.path.join(folder_path, file_name)

        if not os.path.exists(folder_name):
            if not safe_mode:
                os.makedirs(folder_name)  # Create the folder if not in safe_mode
            if verbose:
                print(f"Created folder: {folder_name}")

        # Construct file paths
        src_path = os.path.join(folder_path, file)
        dst_path = os.path.join(folder_name, file)

        if safe_mode:
            # In safe mode, only print what would happen
            print(f"[SAFE MODE] Would move: {src_path} -> {dst_path}")
        else:
            try:
                shutil.move(src_path, dst_path)  # Move the file into the new folder
                organized_files += 1

                if verbose:
                    print(f"Moved: {src_path} -> {dst_path}")
            except Exception as e:
                print(f"Error organizing {file}: {e}")

    # After all operations, report how many files were organized
    if organized_files == 0 and verbose:
        print(f"No files with the extension '{extension}' were found to organize.")
    elif verbose:
        print(f"Total files organized: {organized_files}")


def add_suffix_to_files(folder_path, suffix='_pred', ext='.nii.gz', verbose=False, safe_mode: bool = True):
    """
    Adds a suffix to all files with a specific extension in a folder and its subdirectories.

    Args:
        folder_path (str): The folder where the files are located.
        suffix (str): The suffix to add to the filenames before the extension.
        ext (str): The file extension to search for and rename (default is '.nii.gz').
        safe_mode (bool): If True, simulates the renaming operation without changing any files.
        verbose (bool): If True, prints detailed information about each file being renamed.
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"The directory '{folder_path}' does not exist.")

    renamed_files = 0  # To keep track of how many files were renamed successfully

    # Walk through the folder and its subdirectories
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file has the specified extension
            if file.endswith(ext):
                old_file_path = os.path.join(root, file)
                new_file_name = file.replace(ext, f'{suffix}{ext}')
                new_file_path = os.path.join(root, new_file_name)

                if safe_mode:
                    # In safe mode, print the operation instead of renaming the file
                    print(f"[SAFE MODE] Would rename: {old_file_path} -> {new_file_path}")
                else:
                    try:
                        # Rename the file
                        os.rename(old_file_path, new_file_path)
                        renamed_files += 1

                        if verbose:
                            print(f"Renamed: {old_file_path} -> {new_file_path}")
                    except Exception as e:
                        # Handle errors, like permission issues
                        print(f"Error renaming {old_file_path}: {e}")

    # After all operations, print a summary
    if renamed_files == 0 and verbose:
        print(f"No files with the extension '{ext}' were found to rename.")
    elif verbose:
        print(f"Total files renamed: {renamed_files}")
    print("Renaming completed.")


def add_string_filenames(folder_path, prefix="", suffix="", ext=None, verbose=False):
    """
    Adds a prefix and/or suffix to all files in the specified folder and its subfolders.

    Args:
        folder_path (str): Path to the root folder containing files to rename.
        prefix (str): The prefix to be added to the file names.
        suffix (str): The suffix to be added to the file names (before the extension).
        ext (str): File extension to filter by (e.g., '.nii.gz'). If None, all files are processed.
        verbose (bool): Whether to print verbose output for each rename operation.
    """
    # Walk through all subfolders and files in the given folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file has the specified extension (if provided)
            if ext is None or file.endswith(ext):
                # Construct the old file path
                old_file_path = os.path.join(root, file)

                # Split the file name and apply the prefix/suffix
                name, file_ext = os.path.splitext(file)
                if ext and file.endswith(ext):
                    name = name[: -len(ext)]
                    file_ext = ext

                new_file_name = f"{prefix}{name}{suffix}{file_ext}"

                # Construct the new file path
                new_file_path = os.path.join(root, new_file_name)

                # Rename the file
                os.rename(old_file_path, new_file_path)

                if verbose:
                    print(f"Renaming file: {old_file_path} to {new_file_path}")

    print("Renaming completed.")


def concatenate_csv_files(directory: str, output_file: str):
    """
    Concatenates all CSV files in a specified directory into a single CSV file.

    Args:
        directory: The directory containing the CSV files to concatenate.
        output_file: The path where the concatenated CSV file will be saved.
    """
    csv_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]
    df_list = [pd.read_csv(csv_file) for csv_file in csv_files]
    concatenated_df = pd.concat(df_list, ignore_index=True)
    concatenated_df.to_csv(output_file, index=False)
    print(f"Concatenated CSV files saved to: {output_file}")


def read_datasets_from_dict(name_path_dict: dict, col_name: str = "set") -> pd.DataFrame:
    """
    Reads multiple datasets from a dictionary of name-path pairs and concatenates them into a single DataFrame.

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
