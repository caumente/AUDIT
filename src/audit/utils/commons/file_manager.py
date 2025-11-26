import os
import re
import shutil
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from audit.utils.internal._config_helpers import init_app_yaml
from audit.utils.internal._config_helpers import init_feature_extraction_yaml
from audit.utils.internal._config_helpers import init_metric_extraction_yaml


def create_project_structure(base_path: str = "./"):
    """
    Creates the project directory structure.

    Creates the following structure:
        your_project/
        ├── datasets/
        ├── configs/
        ├── outputs/
        └── logs/

    Parameters
    ----------
    base_path : str, default "./"
        Root directory name where the project structure will be created.

    Raises
    ------
    NotADirectoryError
        If the path exists but is not a directory.
    PermissionError
        If there is no write permission to create folders.
    """
    base = Path(base_path)

    if base.exists() and not base.is_dir():
        raise NotADirectoryError(f"The path '{base}' exists but is not a directory")

    if base.exists() and not base.is_dir() and not base.exists():
        raise PermissionError(f"No write permission to create folders in '{base}'")

    subfolders = ["datasets", "configs", "outputs", "logs"]
    base_path = Path(base_path)

    # Create project folders
    for folder in subfolders:
        path = base_path / folder
        try:
            os.makedirs(path, exist_ok=True)
        except PermissionError:
            print(f"Permission denied: cannot create folder {path}")
        except FileExistsError:
            print(f"A file with the same name already exists: {path}")
        except OSError as e:
            print(f"OS error while creating {path}: {e}")
        else:
            print(f"Folder created or already exists: {path}")

    configs_path = base_path / "configs"
    try:
        # Initialize YAML config files from scratch
        app_file = configs_path / "app.yaml"
        feature_file = configs_path / "feature_extraction.yaml"
        metric_file = configs_path / "metric_extraction.yaml"

        # Only create files if they don't exist (don't overwrite)
        if not app_file.exists():
            init_app_yaml(app_file)
        if not feature_file.exists():
            init_feature_extraction_yaml(feature_file)
        if not metric_file.exists():
            init_metric_extraction_yaml(metric_file)

        print(f"Project structure created under '{base_path}' with default config templates.")

    except Exception as e:
        print(
            f"Error while creating project structure: {e}\n"
            "Check the official documentation to replicate the needed project structure:\n"
            "https://caumente.github.io/AUDIT/getting_started/project_structure/"
        )


def list_dirs(
    path: Union[str, Path], recursive: bool = False, full_path: bool = False, pattern: str = None
) -> List[str]:
    """
    List directories in a given path.

    Parameters
    ----------
    path : str or Path
        The root directory where to look for subdirectories.
    recursive : bool, default False
        If True, search subdirectories recursively.
    full_path : bool, default False
        If True, return absolute paths instead of just directory names.
    pattern : str, optional
        Optional regex pattern to filter directory names.

    Returns
    -------
    List[str]
        A sorted list of directory names or paths.

    Raises
    ------
    FileNotFoundError
        If the specified path does not exist.
    NotADirectoryError
        If the specified path is not a directory.
    PermissionError
        If there is no permission to access the directory.
    """
    root = Path(path)

    if not root.exists():
        raise FileNotFoundError(f"The specified path does not exist: '{root}'")
    if not root.is_dir():
        raise NotADirectoryError(f"The specified path is not a directory: '{root}'")
    if not os.access(root, os.R_OK):
        raise PermissionError(f"No permission to access directory: '{root}'")

    # Get directories
    dirs = root.rglob("*") if recursive else root.iterdir()
    dirs = [d for d in dirs if d.is_dir()]

    # Apply pattern filter if provided
    if pattern:
        regex = re.compile(pattern)
        dirs = [d for d in dirs if regex.search(d.name)]

    # Format output
    result = [str(d.resolve()) if full_path else d.name for d in dirs]

    return sorted(result)


def list_files(
    path: Union[str, Path],
    recursive: bool = False,
    full_path: bool = False,
    pattern: str = None,
    extensions: list[str] | None = None,
) -> List[str]:
    """
    List files in a given directory.

    Parameters
    ----------
    path : str or Path
        Root directory to search.
    recursive : bool, default False
        If True, search subdirectories recursively.
    full_path : bool, default False
        If True, return absolute paths instead of just filenames.
    pattern : str, optional
        Regex pattern to filter file names.
    extensions : list[str] or None, optional
        List of file extensions to filter by (e.g., ['.csv', '.yml']).

    Returns
    -------
    List[str]
        A sorted list of file names or paths.

    Raises
    ------
    FileNotFoundError
        If the specified path does not exist.
    NotADirectoryError
        If the specified path is not a directory.
    PermissionError
        If there is no permission to access the directory.
    """
    root = Path(path)

    if not root.exists():
        raise FileNotFoundError(f"The specified path does not exist: '{root}'")
    if not root.is_dir():
        raise NotADirectoryError(f"The specified path is not a directory: '{root}'")
    if not os.access(root, os.R_OK):
        raise PermissionError(f"No permission to access directory: '{root}'")

    # Get files
    files = root.rglob("*") if recursive else root.iterdir()
    files = [f for f in files if f.is_file()]

    # Filter by regex pattern
    if pattern:
        regex = re.compile(pattern)
        files = [f for f in files if regex.search(f.name)]

    # Filter by extensions
    if extensions:
        extensions = [ext.lower() for ext in extensions]
        files = [f for f in files if f.suffix.lower() in extensions]

    # Format output
    result = [str(f.resolve()) if full_path else f.name for f in files]

    return sorted(result)


def rename_dirs(
    root_dir: Union[str, Path], old_name: str, new_name: str, verbose: bool = False, safe_mode: bool = True
) -> None:
    """
    Rename directories recursively by replacing a substring in their names.

    Parameters
    ----------
    root_dir : str or Path
        Path to the directory where renaming will be performed.
    old_name : str
        The string to be replaced in the directory names.
    new_name : str
        The new string that will replace old_name.
    verbose : bool, default False
        If True, print information about each rename operation.
    safe_mode : bool, default True
        If True, only simulate renaming without making changes.

    Raises
    ------
    FileNotFoundError
        If the specified root_dir does not exist.
    NotADirectoryError
        If the specified root_dir is not a directory.
    PermissionError
        If a directory cannot be renamed due to permissions.
    OSError
        For other OS-level errors during rename.
    """
    root_dir = Path(root_dir)

    if not root_dir.exists():
        raise FileNotFoundError(f"The specified root_dir does not exist: '{root_dir}'")
    if not root_dir.is_dir():
        raise NotADirectoryError(f"The specified root_dir is not a directory: '{root_dir}'")

    # Force verbose if safe_mode is True
    if safe_mode:
        verbose = True

    # Traverse directories from bottom up
    for current_dir, dirs, _ in os.walk(root_dir, topdown=False):
        current_path = Path(current_dir)
        for dir_name in dirs:
            if old_name in dir_name:
                old_dir_path = current_path / dir_name
                new_dir_name = dir_name.replace(old_name, new_name)
                new_dir_path = current_path / new_dir_name

                if safe_mode:
                    print(f"[SAFE MODE] Would rename: {old_dir_path} -> {new_dir_path}")
                else:
                    try:
                        old_dir_path.rename(new_dir_path)
                        if verbose:
                            print(f"Renamed: {old_dir_path} -> {new_dir_path}")
                    except PermissionError as e:
                        raise PermissionError(f"Permission denied: cannot rename '{old_dir_path}'") from e
                    except OSError as e:
                        raise OSError(f"Failed to rename '{old_dir_path}'") from e


def add_string_dirs(
    root_dir: Union[str, Path], prefix: str = "", suffix: str = "", verbose: bool = False, safe_mode: bool = True
) -> None:
    """
    Add a prefix and/or suffix to all directories and subdirectories.

    Parameters
    ----------
    root_dir : str or Path
        Root directory to start renaming.
    prefix : str, default ""
        Prefix to add to directory names.
    suffix : str, default ""
        Suffix to add to directory names.
    verbose : bool, default False
        If True, print information about renamed directories (only when safe_mode=False).
    safe_mode : bool, default True
        If True, simulate renaming without changing directories.

    Raises
    ------
    FileNotFoundError
        If the root directory does not exist.
    NotADirectoryError
        If the root path is not a directory.
    PermissionError
        If a directory cannot be renamed due to permissions.
    OSError
        For other OS-level errors during rename.
    """
    root_dir = Path(root_dir)

    if not root_dir.exists():
        raise FileNotFoundError(f"The specified root_dir does not exist: '{root_dir}'")
    if not root_dir.is_dir():
        raise NotADirectoryError(f"The specified root_dir is not a directory: '{root_dir}'")

    # Force verbose if safe_mode
    if safe_mode:
        verbose = True

    # Bottom-up traversal
    for current_dir, dirs, _ in os.walk(root_dir, topdown=False):
        current_path = Path(current_dir)
        for dir_name in dirs:
            old_dir_path = current_path / dir_name
            new_dir_name = f"{prefix}{dir_name}{suffix}"
            new_dir_path = current_path / new_dir_name

            if old_dir_path != new_dir_path:
                if safe_mode:
                    print(f"[SAFE MODE] Would rename: {old_dir_path} -> {new_dir_path}")
                else:
                    try:
                        old_dir_path.rename(new_dir_path)
                        if verbose:
                            print(f"Renamed: {old_dir_path} -> {new_dir_path}")
                    except PermissionError as e:
                        raise PermissionError(f"Permission denied: cannot rename '{old_dir_path}'") from e
                    except OSError as e:
                        raise OSError(f"Failed to rename '{old_dir_path}'") from e


def rename_files(
    root_dir: Union[str, Path], old_name: str = "", new_name: str = "", verbose: bool = False, safe_mode: bool = True
) -> None:
    """
    Recursively rename files by replacing a substring in their filenames.

    Parameters
    ----------
    root_dir : str or Path
        Root directory to start renaming files.
    old_name : str, default ""
        Substring in filenames to replace.
    new_name : str, default ""
        Substring to replace old_name with.
    verbose : bool, default False
        If True, print information about renamed files (only when safe_mode=False).
    safe_mode : bool, default True
        If True, simulate renaming without changing files.

    Raises
    ------
    ValueError
        If old_name or new_name are empty strings.
    FileNotFoundError
        If the specified root_dir does not exist.
    NotADirectoryError
        If the specified root_dir is not a directory.
    PermissionError
        If a file cannot be renamed due to permissions.
    OSError
        For other OS-level errors during rename.
    """
    if not old_name or not new_name:
        raise ValueError("Both 'old_name' and 'new_name' must be non-empty strings")

    root_dir = Path(root_dir)
    if not root_dir.exists():
        raise FileNotFoundError(f"The specified root_dir does not exist: '{root_dir}'")
    if not root_dir.is_dir():
        raise NotADirectoryError(f"The specified root_dir is not a directory: '{root_dir}'")

    # Force verbose if safe_mode
    if safe_mode:
        verbose = True

    # Walk through all files
    for current_dir, _, files in os.walk(root_dir):
        current_path = Path(current_dir)
        for file_name in files:
            if old_name in file_name:
                old_file_path = current_path / file_name
                new_file_name = file_name.replace(old_name, new_name)
                new_file_path = current_path / new_file_name

                if safe_mode:
                    print(f"[SAFE MODE] Would rename: {old_file_path} -> {new_file_path}")
                else:
                    try:
                        old_file_path.rename(new_file_path)
                        if verbose:
                            print(f"Renamed: {old_file_path} -> {new_file_path}")
                    except PermissionError as e:
                        raise PermissionError(f"Permission denied: cannot rename '{old_file_path}'") from e
                    except OSError as e:
                        raise OSError(f"Failed to rename '{old_file_path}'") from e


def copy_files_by_extension(
    src_dir: str, dst_dir: str, ext: str, safe_mode: bool = True, overwrite: bool = False, verbose: bool = False
):
    """
    Copy all files with a specific extension from one directory to another.

    Parameters
    ----------
    src_dir : str
        The source directory from which to copy files.
    dst_dir : str
        The destination directory where files will be copied.
    ext : str
        The file extension to search for and copy (e.g., ".txt", ".yaml").
    safe_mode : bool, default True
        If True, simulate the operation without making changes.
    overwrite : bool, default False
        If True, allow overwriting existing files in the destination directory.
    verbose : bool, default False
        If True, print detailed logs for each file operation.

    Raises
    ------
    ValueError
        If the source directory does not exist.
    """
    if not os.path.exists(src_dir):
        raise ValueError(f"Source directory '{src_dir}' does not exist.")

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
                        shutil.copy2(src_file_path, dst_file_path)
                        copied_files += 1
                        if verbose:
                            print(f"Copied: {src_file_path} -> {dst_file_path}")
                    except Exception as e:
                        print(f"Error copying {src_file_path} to {dst_file_path}: {e}")

    # Summary after processing all files
    if copied_files == 0 and verbose:
        print(f"No files with the extension '{ext}' were found to copy.")
    elif verbose:
        print(f"Total files copied: {copied_files}")


def delete_files_by_extension(root_dir: str, ext: str, verbose: bool = False, safe_mode: bool = True):
    """
    Deletes all files with a specific extension in a path and its subdirectories.

    Parameters
    ----------
    root_dir : str
        The root directory where the search will start.
    ext : str
        The file extension of the files to be deleted (e.g., '.nii.gz').
    verbose : bool, default False
        If True, print detailed logs for each file deletion operation.
    safe_mode : bool, default True
        If True, simulate the deletion without actually removing the files.

    Raises
    ------
    ValueError
        If the root_dir does not exist.
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        raise ValueError(f"Root directory '{root_dir}' does not exist.")

    deleted_count = 0

    # Walk through the directory tree
    for subdir, _, files in os.walk(root_path):
        for file in sorted(files):
            if file.endswith(ext):
                file_path = Path(subdir) / file

                if safe_mode:
                    print(f"[SAFE MODE] Would delete: {file_path}")
                else:
                    try:
                        file_path.unlink()  # Delete the file
                        deleted_count += 1
                        if verbose:
                            print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

    # Summary
    if deleted_count == 0 and verbose:
        print(f"No files with the extension '{ext}' were found to delete.")
    elif verbose:
        print(f"Total files deleted: {deleted_count}")


def delete_dirs_by_pattern(
    root_dir: str, pattern: str, match_type: str = "contains", verbose: bool = False, safe_mode: bool = True
):
    """
    Deletes folders matching a pattern in a path and its subdirectories.

    Parameters
    ----------
    root_dir : str
        Directory where the search will start.
    pattern : str
        Pattern to match folder names.
    match_type : str, default 'contains'
        Type of matching: 'contains', 'starts', 'ends', or 'exact'.
    verbose : bool, default False
        If True, print detailed logs for each folder deletion operation.
    safe_mode : bool, default True
        If True, simulate deletion without actually removing folders.

    Raises
    ------
    ValueError
        If root_dir does not exist or match_type is invalid.
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        raise ValueError(f"Root directory '{root_dir}' does not exist.")

    allowed_match_types = ["contains", "starts", "ends", "exact"]
    if match_type not in allowed_match_types:
        raise ValueError(f"match_type must be one of {allowed_match_types}, got '{match_type}'")

    deleted_count = 0
    found_folders = []

    # Walk the directory tree from bottom up
    for subdir, dirs, _ in os.walk(root_path, topdown=False):
        for dir_name in sorted(dirs):
            match = False
            if match_type == "contains" and pattern in dir_name:
                match = True
            elif match_type == "starts" and dir_name.startswith(pattern):
                match = True
            elif match_type == "ends" and dir_name.endswith(pattern):
                match = True
            elif match_type == "exact" and dir_name == pattern:
                match = True

            if match:
                folder_path = Path(subdir) / dir_name
                found_folders.append(folder_path)

                if safe_mode:
                    if verbose:
                        print(f"[SAFE MODE] Would delete: {folder_path}")
                else:
                    try:
                        shutil.rmtree(folder_path)
                        deleted_count += 1
                        if verbose:
                            print(f"Deleted folder: {folder_path}")
                    except Exception as e:
                        print(f"Error deleting {folder_path}: {e}")

    # Summary
    if safe_mode and verbose:
        print(f"[SAFE MODE] {len(found_folders)} folders would be deleted.")
    elif not safe_mode:
        if deleted_count == 0 and verbose:
            print(f"No folders matching the pattern '{pattern}' were found to delete.")
        elif verbose:
            print(f"Total folders deleted: {deleted_count}")


def move_files_to_parent(
    root_dir: str, levels_up: int = 1, ext: str | None = None, verbose: bool = False, safe_mode: bool = True
) -> None:
    """
    Move files (optionally filtered by extension) from subdirectories
    to a specified parent level above their current location.

    Parameters
    ----------
    root_dir : str
        Root directory where the search will start.
    levels_up : int, default 1
        Number of parent levels up to move the files.
    ext : str or None, optional
        File extension to filter by (e.g., ".txt"). If None, all files are moved.
    verbose : bool, default False
        If True, print detailed logs for each file move operation.
    safe_mode : bool, default True
        If True, simulate the move without actually moving the files.

    Raises
    ------
    FileNotFoundError
        If root_dir does not exist.
    ValueError
        If levels_up is less than 1.
    """
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"Root directory '{root_dir}' does not exist.")

    if levels_up < 1:
        raise ValueError("'levels_up' must be at least 1.")

    moved_files = 0

    # Walk through the directory tree
    for subdir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()

        # Compute the target directory
        target_dir = subdir
        for _ in range(levels_up):
            target_dir = os.path.dirname(target_dir)

        if not target_dir or not os.path.exists(target_dir):
            if verbose:
                print(f"Skipping {subdir}: invalid or non-existing target directory.")
            continue

        for file_name in files:
            if ext is None or file_name.endswith(ext):
                source = os.path.join(subdir, file_name)
                destination = os.path.join(target_dir, file_name)

                if safe_mode:
                    print(f"[SAFE MODE] Would move: {source} -> {destination}")
                else:
                    try:
                        shutil.move(source, destination)
                        moved_files += 1
                        if verbose:
                            print(f"Moved: {source} -> {destination}")
                    except Exception as e:
                        print(f"Error moving {source} -> {destination}: {e}")

    if safe_mode:
        print("Safe mode enabled: No files were moved.")
    elif verbose:
        if moved_files == 0:
            print("No files were moved.")
        else:
            print(f"Total files moved: {moved_files}")


def organize_files_into_dirs(root_dir, extension=".nii.gz", verbose=False, safe_mode: bool = True):
    """
    Organizes files into folders based on their filenames. Each file will be moved into a folder named
    after the file (excluding the extension).

    Parameters
    ----------
    root_dir : str
        Directory containing the files to organize.
    extension : str, default '.nii.gz'
        The file extension to look for.
    verbose : bool, default False
        If True, print detailed logs about each file being organized.
    safe_mode : bool, default True
        If True, simulate the file organization without moving the files.

    Raises
    ------
    ValueError
        If the root_dir does not exist.

    Examples
    --------
    Suppose 'root_dir' contains:
        subj1.nii.gz
        subj2.nii.gz

    After running:
        organize_files_into_dirs(root_dir, extension='.nii.gz', safe_mode=False)

    The folder structure will become:
        root_dir/
        ├── subj1/
        │   └── subj1.nii.gz
        └── subj2/
            └── subj2.nii.gz
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"The directory '{root_dir}' does not exist.")

    # List all files in the given folder
    files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]

    organized_files = 0

    for file in files:
        if not file.endswith(extension):
            continue  # Skip files that don't match the extension

        # Extract file name without extension
        file_name = file[: -len(extension)] if extension else os.path.splitext(file)[0]

        folder_name = os.path.join(root_dir, file_name)

        if not os.path.exists(folder_name):
            if not safe_mode:
                os.makedirs(folder_name)
            if verbose:
                print(f"Created folder: {folder_name}")

        src_path = os.path.join(root_dir, file)
        dst_path = os.path.join(folder_name, file)

        if safe_mode:
            print(f"[SAFE MODE] Would move: {src_path} -> {dst_path}")
        else:
            try:
                shutil.move(src_path, dst_path)
                organized_files += 1
                if verbose:
                    print(f"Moved: {src_path} -> {dst_path}")
            except Exception as e:
                print(f"Error organizing {file}: {e}")

    if organized_files == 0 and verbose:
        print(f"No files with the extension '{extension}' were found to organize.")
    elif verbose:
        print(f"Total files organized: {organized_files}")


def organize_subdirs_into_named_dirs(
    root_dir: str, join_char: str = "-", verbose: bool = False, safe_mode: bool = True
) -> Dict[str, List[str]]:
    """
    Organizes subfolders into combined named folders.
    Combines parent folder names and their subfolder names into a single folder per subfolder.

    Parameters
    ----------
    root_dir : str
        Directory containing the parent folders.
    join_char : str, default "-"
        Character to join parent and subfolder names.
    verbose : bool, default False
        If True, print detailed logs about each operation.
    safe_mode : bool, default True
        If True, simulate the folder organization without making changes.

    Returns
    -------
    Dict[str, List[str]]
        Summary of operations performed or simulated.
        Keys: "created_folders", "moved_items", "removed_folders"

    Raises
    ------
    ValueError
        If the root_dir does not exist.

    Examples
    --------
    Input:
        DATASET_images/
        └── Patient-002/
            ├── timepoint-000/
            ├── timepoint-001/

    Output:
        DATASET_images/
        ├── Patient-002-timepoint-000/
        ├── Patient-002-timepoint-001/
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        raise ValueError(f"The directory '{root_dir}' does not exist.")

    summary = {"created_folders": [], "moved_items": [], "removed_folders": []}

    parent_dirs = [d for d in sorted(root_path.iterdir()) if d.is_dir()]

    for parent_dir in parent_dirs:
        subdirs = [d for d in sorted(parent_dir.iterdir()) if d.is_dir()]

        for subdir in subdirs:
            new_folder_name = f"{parent_dir.name}{join_char}{subdir.name}"
            new_folder_path = root_path / new_folder_name

            if not new_folder_path.exists():
                if not safe_mode:
                    new_folder_path.mkdir()
                summary["created_folders"].append(str(new_folder_path))
                if verbose:
                    print(f"Created folder: {new_folder_path}")

            for item in subdir.iterdir():
                dest = new_folder_path / item.name
                if safe_mode:
                    if verbose:
                        print(f"[SAFE MODE] Would move: {item} -> {dest}")
                else:
                    try:
                        shutil.move(str(item), str(dest))
                        summary["moved_items"].append(f"{item} -> {dest}")
                        if verbose:
                            print(f"Moved: {item} -> {dest}")
                    except Exception as e:
                        print(f"Error moving {item} -> {dest}: {e}")

            if not safe_mode:
                try:
                    subdir.rmdir()
                    summary["removed_folders"].append(str(subdir))
                    if verbose:
                        print(f"Removed empty folder: {subdir}")
                except Exception as e:
                    print(f"Error removing folder {subdir}: {e}")

        if not safe_mode and not any(parent_dir.iterdir()):
            try:
                parent_dir.rmdir()
                summary["removed_folders"].append(str(parent_dir))
                if verbose:
                    print(f"Removed empty parent folder: {parent_dir}")
            except Exception as e:
                print(f"Error removing parent folder {parent_dir}: {e}")

    return summary


def add_suffix_to_files(root_dir, suffix="_pred", ext=".nii.gz", verbose=False, safe_mode: bool = True):
    """
    Adds a suffix to all files with a specific extension in a folder and its subdirectories.

    Parameters
    ----------
    root_dir : str
        The folder where the files are located.
    suffix : str, default '_pred'
        The suffix to add to the filenames before the extension.
    ext : str, default '.nii.gz'
        The file extension to search for and rename.
    verbose : bool, default False
        If True, print detailed information about each file being renamed.
    safe_mode : bool, default True
        If True, simulate the renaming operation without changing any files.

    Raises
    ------
    ValueError
        If the root_dir does not exist.
    """
    if not os.path.exists(root_dir):
        raise ValueError(f"The directory '{root_dir}' does not exist.")

    renamed_files = 0  # To keep track of how many files were renamed successfully

    # Walk through the folder and its subdirectories
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # Check if the file has the specified extension
            if file.endswith(ext):
                old_file_path = os.path.join(root, file)
                new_file_name = file.replace(ext, f"{suffix}{ext}")
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


def add_string_files(
    root_dir: Union[str, Path],
    prefix: str = "",
    suffix: str = "",
    ext: Optional[str] = None,
    verbose: bool = False,
    safe_mode: bool = True,
) -> None:
    """
    Add a prefix and/or suffix to all files in a folder and its subfolders.

    Parameters
    ----------
    root_dir : str or Path
        Directory containing files to rename.
    prefix : str, default ""
        Prefix to add to the file name (before the stem).
    suffix : str, default ""
        Suffix to add to the file name (after the stem, before extension).
    ext : str or None, optional
        If provided, treat this exact string as the file extension (supports multi-part
        extensions like '.nii.gz'). The extension match is done using `str.endswith(ext)`.
        If None, all files are processed and `os.path.splitext` is used to separate stem/ext.
        If used, should include the leading dot(s), e.g. '.nii.gz' or '.txt'.
    verbose : bool, default False
        If True, print information about actual renames (only when safe_mode=False).
    safe_mode : bool, default True
        If True, simulate renames and print planned operations (no filesystem changes).

    Raises
    ------
    FileNotFoundError
        If root_dir does not exist.
    NotADirectoryError
        If root_dir exists but is not a directory.
    PermissionError
        If a rename fails due to permissions.
    FileExistsError
        If the target file already exists.
    OSError
        For other OS-level errors during rename.
    """
    root = Path(root_dir)

    if not root.exists():
        raise FileNotFoundError(f"The specified root_dir does not exist: '{root}'")
    if not root.is_dir():
        raise NotADirectoryError(f"The specified root_dir is not a directory: '{root}'")

    # Force verbose when simulating so the user sees the planned actions
    if safe_mode:
        verbose = True

    for current_dir, _, files in os.walk(root):
        current_path = Path(current_dir)
        for file in files:
            # Filter by extension (if provided)
            if ext is None or file.endswith(ext):
                old_file_path = current_path / file

                # Respect multi-part ext if provided, otherwise use splitext
                if ext and file.endswith(ext):
                    name = file[: -len(ext)]
                    file_ext = ext
                else:
                    name, file_ext = os.path.splitext(file)

                new_file_name = f"{prefix}{name}{suffix}{file_ext}"
                new_file_path = current_path / new_file_name

                # Skip if no-op
                if old_file_path == new_file_path:
                    continue

                if safe_mode:
                    print(f"[SAFE MODE] Would rename: {old_file_path} -> {new_file_path}")
                else:
                    if new_file_path.exists():
                        raise FileExistsError(f"Target already exists: '{new_file_path}'")
                    try:
                        old_file_path.rename(new_file_path)
                        if verbose:
                            print(f"Renamed: {old_file_path} -> {new_file_path}")
                    except PermissionError as e:
                        raise PermissionError(f"Permission denied: cannot rename '{old_file_path}'") from e
                    except OSError as e:
                        raise OSError(f"Failed to rename '{old_file_path}' to '{new_file_path}': {e}") from e
