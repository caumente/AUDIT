import os
import re
import shutil
from typing import Any
from pathlib import Path

import pandas as pd
import yaml


def list_dirs(path: str) -> list:
    """
    Lists all directories within a given root_dir and returns their names in sorted order.

    Args:
        path: The path root_dir where to look for subdirectories.

    Returns:
        list: A sorted list of path names found within the specified root_dir.
    """
    try:
        return sorted([f.path.split("/")[-1] for f in os.scandir(path) if f.is_dir()])
    except FileNotFoundError:
        print(f"Error: The root_dir '{path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
        return []


def list_files(path: str) -> list:
    """
    Lists all files within a given root_dir and returns their names in sorted order.

    Args:
        path: The path root_dir where to look for files.

    Returns:
        list: A sorted list of files names found within the specified root_dir.
    """
    try:
        return sorted([f.path.split("/")[-1] for f in os.scandir(path) if f.is_file()])
    except FileNotFoundError:
        print(f"Error: The root_dir '{path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
        return []


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


def rename_directories(root_dir: str, old_name: str, new_name: str, verbose: bool = False, safe_mode: bool = True):
    """
    Renames all directories and subdirectories within a path,
    replacing string_1 with string_2 in their names.

    Args:
        root_dir (str): Path to the path where renaming will be performed.
        old_name (str): The string to be replaced in the path names.
        new_name (str): The new string that will replace string_1.
        verbose (bool): Whether to print verbose output for each rename operation.
        safe_mode (bool): If True, only simulates renaming without making changes.
    """

    if not os.path.exists(root_dir):
        raise ValueError(f"The specified root_dir {root_dir} does not exist.")

    # Traverse the path tree, renaming directories from the bottom up
    for root, dirs, files in os.walk(root_dir, topdown=False):
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
        print(f"Set safe_mode parameter to False to rename the directories")


def add_string_directories(root_dir: str, prefix: str = "", suffix: str = "", verbose: bool = False, safe_mode: bool = True):
    """
    Adds a prefix and/or suffix to all directories and subdirectories within a path.

    Args:
        root_dir (str): Path to the path where renaming will be performed.
        prefix (str): The prefix to be added to the path names.
        suffix (str): The suffix to be added to the path names.
        verbose (bool): Whether to print verbose output for each rename operation.
        safe_mode (bool): If True, only simulates renaming without making changes.
    """
    # Traverse the path tree, renaming directories from the bottom up
    for root, dirs, files in os.walk(root_dir, topdown=False):
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


def rename_files(root_dir: str, old_name: str = "_t1ce", new_name: str = "_t1c", verbose: bool = False, safe_mode: bool = True):
    """
    Renames files in a path and its subdirectories by replacing a specific substring in the filenames.

    This function recursively walks through all files in a specified root_dir path and its subdirectories,
    identifies files containing a specified old extension substring, and renames them by replacing
    the old extension with a new one.

    Args:
        root_dir: The root_dir path containing the files to be renamed.
        old_name: The substring in filenames that needs to be replaced. Defaults to "_t1ce".
        new_name: The substring that will replace the old extension. Defaults to "_t1c".
        verbose: Whether print the log
        safe_mode: If True, the function will only simulate renaming without making any actual changes.
    """
    if old_name is None:
        old_name = ""

    if new_name is None:
        new_name = ""

    for subdir, _, files in os.walk(root_dir):
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
    Copies all files with a specific extension from one path to another.

    Args:
        src_dir (str): The source path from which to copy files.
        dst_dir (str): The destination path where files will be copied.
        ext (str): The file extension to search for and copy (e.g., ".txt", ".yaml").
        safe_mode (bool): If True, simulates the operation without making changes.
        overwrite (bool): If True, allows overwriting existing files in the destination path.
        verbose (bool): If True, prints detailed logs for each file operation.
    """

    if not os.path.exists(src_dir):
        raise ValueError(f"Source path '{src_dir}' does not exist.")

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)  # Ensure destination path exists

    copied_files = 0  # To keep track of how many files have been copied
    for subdir, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(ext):
                src_file_path = os.path.join(subdir, file)
                dst_file_path = os.path.join(dst_dir, file)

                # Check if the file already exists in the destination path
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
    Deletes all files with a specific extension in a path and its subdirectories.

    Args:
        root_dir (str): The root_dir path where the search will start.
        ext (str): The file extension of the files to be deleted.
        safe_mode (bool): If True, simulates the deletion without actually removing the files.
        verbose (bool): If True, prints detailed logs for each file deletion operation.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"Root path '{root_dir}' does not exist.")

    deleted_files = 0  # To keep track of how many files have been deleted

    # Walk through the path tree
    for subdir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()

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


def delete_folders_by_pattern(root_dir: str, pattern: str, verbose=False, safe_mode: bool = True):
    """
    Deletes all folders that match a given pattern in a path and its subdirectories.

    Args:
        root_dir (str): The root_dir path where the search will start.
        pattern (str): The pattern to match folder names (supports regular expressions).
        safe_mode (bool): If True, simulates the deletion without actually removing the folders.
        verbose (bool): If True, prints detailed logs for each folder deletion operation.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"Root path '{root_dir}' does not exist.")

    deleted_folders = 0  # To keep track of how many folders have been deleted
    regex_pattern = re.compile(pattern)  # Compile the provided pattern for use in matching folder names

    # Walk through the path tree
    for subdir, dirs, _ in os.walk(root_dir, topdown=False):  # topdown=False ensures subdirectories are checked first

        for dir_name in dirs:
            if regex_pattern.match(dir_name):  # Match folder name with the regex pattern
                folder_path = os.path.join(subdir, dir_name)

                if safe_mode:
                    # In safe mode, only print what would happen
                    print(f"[SAFE MODE] Would delete: {folder_path}")
                else:
                    try:
                        shutil.rmtree(folder_path)  # Delete the folder and its contents
                        deleted_folders += 1

                        if verbose:
                            print(f"Deleted folder: {folder_path}")
                    except Exception as e:
                        print(f"Error deleting {folder_path}: {e}")

    # After all operations, report how many folders were deleted
    if deleted_folders == 0 and verbose:
        print(f"No folders matching the pattern '{pattern}' were found to delete.")
    elif verbose:
        print(f"Total folders deleted: {deleted_folders}")


def move_files_to_parent(root_dir: str, levels_up: int = 1, ext: str = None, verbose: bool = False, safe_mode: bool = True):
    """
    Move all files or files with a specific extension from subdirectories to a specified parent level path.

    Args:
        root_dir (str): The root_dir path where the search will start.
        levels_up (int): Number of parent levels up to move the files.
        ext (str): Specific file extension to move (e.g., ".txt"). If None, moves all files.
        verbose (bool): If True, prints detailed logs for each file move operation.
        safe_mode (bool): If True, simulates the move without actually moving the files.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"Root path '{root_dir}' does not exist.")

    if levels_up < 1:
        raise ValueError("'levels_up' must be at least 1.")

    moved_files = 0  # To keep track of how many files have been moved

    # Walk through the path tree
    for subdir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()

        # Determine the target parent path
        target_dir = subdir
        for _ in range(levels_up):
            target_dir = os.path.dirname(target_dir)

        if not target_dir or not os.path.exists(target_dir):
            if verbose:
                print(f"Skipping {subdir} as target path does not exist or is invalid.")
            continue

        for file_name in files:
            if ext is None or file_name.endswith(ext):
                source = os.path.join(subdir, file_name)
                destination = os.path.join(target_dir, file_name)

                if safe_mode:
                    # In safe mode, only print what would happen
                    if verbose:
                        print(f"[SAFE MODE] Would move: {source} to {destination}")
                else:
                    try:
                        shutil.move(source, destination)  # Move the file
                        moved_files += 1

                        if verbose:
                            print(f"Moved file: {source} to {destination}")
                    except Exception as e:
                        print(f"Error moving {source} to {destination}: {e}")

    # After all operations, report how many files were moved
    if moved_files == 0 and verbose:
        print("No files were moved.")
    elif verbose:
        print(f"Total files moved: {moved_files}")


def organize_files_into_folders(root_dir, extension='.nii.gz', verbose=False, safe_mode: bool = True):
    """
    Organizes files into folders based on their filenames. Each file will be moved into a folder named
    after the file (excluding the extension).

    Args:
        root_dir (str): Path to the folder containing the files.
        extension (str): The file extension to look for (default is '.nii.gz').
        safe_mode (bool): If True, simulates the file organization without moving the files.
        verbose (bool): If True, prints detailed logs about each file being organized.
    """

    if not os.path.exists(root_dir):
        raise ValueError(f"The path '{root_dir}' does not exist.")

    # List all files in the given folder
    files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]

    organized_files = 0  # Counter to keep track of how many files were organized

    for file in files:
        # Extract the file name without extension
        file_name = file.split(extension)[0]

        # Create a new folder for the file
        folder_name = os.path.join(root_dir, file_name)

        if not os.path.exists(folder_name):
            if not safe_mode:
                os.makedirs(folder_name)  # Create the folder if not in safe_mode
            if verbose:
                print(f"Created folder: {folder_name}")

        # Construct file paths
        src_path = os.path.join(root_dir, file)
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


def organize_subfolders_into_named_folders(root_dir, join_char="-", verbose=False, safe_mode: bool = True):
    """
    Organizes subfolders into combined named folders.
    Dynamically combines parent folder names and their subfolder names into a single folder per subfolder.
    Useful for longitudinal data:
    Input:
        DATASET_images/
        └── Patient-002/
            ├── timepoint-000/
            │   ├── t1.nii.gz
            │   ├── ..
            ├── timepoint-001/
            │   ├── t1.nii.gz
            │   ├── ..
            ├── timepoint-002/
            │   ├── t1.nii.gz

    Output:
        DATASET_images/
        ├── Patient-002-timepoint-000/
        │   ├── t1.nii.gz
        │   ├── ..
        ├── Patient-002-timepoint-001/
        │   ├── t1.nii.gz
        │   ├── ..
        ├── Patient-002-timepoint-002/
        │   ├── t1.nii.gz

        Args:
        root_dir (str): Path to the folder containing the parent folders.
        join_char (str): The character to use when joining the parent folder and subfolder names (default is "-").
        verbose (bool): If True, prints detailed logs about each folder being organized.
        safe_mode (bool): If True, simulates the folder organization without making changes.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"The path '{root_dir}' does not exist.")

    # List all subdirectories in the main folder
    parent_directories = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]

    for parent_dir in sorted(parent_directories):
        parent_dir_path = os.path.join(root_dir, parent_dir)

        # List all subdirectories under the parent path
        subdirectories = [d for d in os.listdir(parent_dir_path) if os.path.isdir(os.path.join(parent_dir_path, d))]

        for subdir in subdirectories:
            subdir_path = os.path.join(parent_dir_path, subdir)

            # Create the new folder name using the specified join character
            new_folder_name = f"{parent_dir}{join_char}{subdir}"
            new_folder_path = os.path.join(root_dir, new_folder_name)

            if not os.path.exists(new_folder_path):
                if not safe_mode:
                    os.makedirs(new_folder_path)  # Create the folder if not in safe_mode
                if verbose:
                    print(f"Created folder: {new_folder_path}")

            # Move all contents from the subfolder to the new folder
            for item in os.listdir(subdir_path):
                item_path = os.path.join(subdir_path, item)
                new_item_path = os.path.join(new_folder_path, item)

                if safe_mode:
                    print(f"[SAFE MODE] Would move: {item_path} -> {new_item_path}")
                else:
                    try:
                        shutil.move(item_path, new_item_path)
                        if verbose:
                            print(f"Moved: {item_path} -> {new_item_path}")
                    except Exception as e:
                        print(f"Error moving {item_path}: {e}")

            # Remove the now-empty subfolder if not in safe_mode
            if not safe_mode:
                try:
                    os.rmdir(subdir_path)
                    if verbose:
                        print(f"Removed empty folder: {subdir_path}")
                except Exception as e:
                    print(f"Error removing folder {subdir_path}: {e}")

        # After processing all subfolders, remove the now-empty parent path
        if not safe_mode:
            try:
                if not os.listdir(parent_dir_path):  # Check if the folder is empty
                    os.rmdir(parent_dir_path)
                    if verbose:
                        print(f"Removed empty parent folder: {parent_dir_path}")
            except Exception as e:
                print(f"Error removing parent folder {parent_dir_path}: {e}")


def add_suffix_to_files(root_dir, suffix='_pred', ext='.nii.gz', verbose=False, safe_mode: bool = True):
    """
    Adds a suffix to all files with a specific extension in a folder and its subdirectories.

    Args:
        root_dir (str): The folder where the files are located.
        suffix (str): The suffix to add to the filenames before the extension.
        ext (str): The file extension to search for and rename (default is '.nii.gz').
        safe_mode (bool): If True, simulates the renaming operation without changing any files.
        verbose (bool): If True, prints detailed information about each file being renamed.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"The path '{root_dir}' does not exist.")

    renamed_files = 0  # To keep track of how many files were renamed successfully

    # Walk through the folder and its subdirectories
    for root, dirs, files in os.walk(root_dir):
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
    if renamed_files == 0:
        print(f"No files with the extension '{ext}' were found to rename.")
    else:
        print(f"Total files renamed: {renamed_files}")


def add_string_filenames(root_dir, prefix="", suffix="", ext=None, verbose=False, safe_mode=True):
    """
    Adds a prefix and/or suffix to all files in the specified folder and its subfolders.

    Args:
        root_dir (str): Path to the root_dir folder containing files to rename.
        prefix (str): The prefix to be added to the file names.
        suffix (str): The suffix to be added to the file names (before the extension).
        ext (str): File extension to filter by (e.g., '.nii.gz'). If None, all files are processed.
        verbose (bool): Whether to print verbose output for each rename operation.
        safe_mode (bool): If True, simulates the renaming without applying changes.
    """
    # Walk through all subfolders and files in the given folder
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # Check if the file has the specified extension (if provided)
            if ext is None or file.endswith(ext):
                # Construct the old file root_dir
                old_file_path = os.path.join(root, file)

                # Properly split the filename and extension
                if ext and file.endswith(ext):
                    name = file[: -len(ext)]  # Extract the name without the custom extension
                    file_ext = ext
                else:
                    name, file_ext = os.path.splitext(file)  # Use regular splitting for standard extensions

                # Apply the prefix and/or suffix
                new_file_name = f"{prefix}{name}{suffix}{file_ext}"

                # Construct the new file root_dir
                new_file_path = os.path.join(root, new_file_name)

                if safe_mode:
                    print(f"[SAFE MODE] Would rename: {old_file_path} -> {new_file_path}")
                else:
                    # Perform the actual renaming
                    try:
                        os.rename(old_file_path, new_file_path)
                        if verbose:
                            print(f"Renamed: {old_file_path} -> {new_file_path}")
                    except Exception as e:
                        print(f"Error renaming {old_file_path}: {e}")

    if safe_mode:
        print("Safe mode enabled: No files were renamed.")
    else:
        print("Renaming completed.")


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
