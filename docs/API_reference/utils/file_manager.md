# File Manager API Reference

The `file_manager` module provides a comprehensive set of utilities for **file and directory management**.  
It supports listing, renaming, moving, copying, deleting, and organizing files/folders, as well as reading/writing datasets and configuration files.

---

## Module Overview
- **Listing**: Enumerate files and directories.
- **Configuration**: Load YAML config files with variable substitution.
- **File & Directory Operations**: Rename, add prefixes/suffixes, delete, copy, move.
- **Organizing**: Restructure files/folders for dataset preparation.
- **CSV Handling**: Concatenate multiple CSVs, load datasets into DataFrames.

Most modification functions support:
- **`safe_mode`** → simulate changes without executing them.
- **`verbose`** → detailed logs of operations.

---

## Functions

### 🔍 Listing

#### `list_dirs(path: str) -> list`
List all **subdirectories** inside a given path.

- **Parameters**
  - `path` *(str)*: Path to search for subdirectories.
- **Returns**
  - *(list)*: Sorted list of directory names.
- **Raises**
  - Prints errors if the path does not exist or permission is denied.

---

#### `list_files(path: str) -> list`
List all **files** inside a given path.

- **Parameters**
  - `path` *(str)*: Path to search for files.
- **Returns**
  - *(list)*: Sorted list of filenames.
- **Raises**
  - Prints errors if the path does not exist or permission is denied.

---

### ⚙️ Configuration

#### `load_config_file(path: str) -> dict`
Load a YAML configuration file and substitute variables of the form `${VAR}`.

- **Parameters**
  - `path` *(str)*: Relative path to the YAML configuration file.
- **Returns**
  - *(dict)*: Parsed YAML content with variables resolved.
- **Raises**
  - `FileNotFoundError`: If the file does not exist.

---

### 📝 Directory Operations

#### `rename_directories(root_dir: str, old_name: str, new_name: str, verbose=False, safe_mode=True)`
Rename all directories and subdirectories by replacing a substring in their names.

- **Parameters**
  - `root_dir` *(str)*: Root path where renaming starts.
  - `old_name` *(str)*: Substring to replace.
  - `new_name` *(str)*: Replacement string.
  - `verbose` *(bool)*: Print details if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

#### `add_string_directories(root_dir: str, prefix="", suffix="", verbose=False, safe_mode=True)`
Add prefix/suffix to all directories recursively.

- **Parameters**
  - `root_dir` *(str)*: Path where renaming starts.
  - `prefix` *(str)*: String to prepend.
  - `suffix` *(str)*: String to append.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

### 📝 File Operations

#### `rename_files(root_dir: str, old_name="_t1ce", new_name="_t1c", verbose=False, safe_mode=True)`
Rename files by replacing a substring.

- **Parameters**
  - `root_dir` *(str)*: Path where renaming starts.
  - `old_name` *(str)*: Substring to replace.
  - `new_name` *(str)*: Replacement string.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

#### `add_suffix_to_files(root_dir: str, suffix="_pred", ext=".nii.gz", verbose=False, safe_mode=True)`
Append a suffix to filenames before the extension.

- **Parameters**
  - `root_dir` *(str)*: Path to scan.
  - `suffix` *(str)*: Suffix to add.
  - `ext` *(str)*: Target extension.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

#### `add_string_filenames(root_dir: str, prefix="", suffix="", ext=None, verbose=False, safe_mode=True)`
Add prefix/suffix to filenames.

- **Parameters**
  - `root_dir` *(str)*: Path to scan.
  - `prefix` *(str)*: String to prepend.
  - `suffix` *(str)*: String to append.
  - `ext` *(str or None)*: If set, only process files with this extension.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

### 📤 Copying & Moving

#### `copy_files_by_extension(src_dir: str, dst_dir: str, ext: str, safe_mode=True, overwrite=False, verbose=False)`
Copy all files of a given extension.

- **Parameters**
  - `src_dir` *(str)*: Source path.
  - `dst_dir` *(str)*: Destination path.
  - `ext` *(str)*: File extension (e.g. `.txt`).
  - `safe_mode` *(bool)*: Simulate only if `True`.
  - `overwrite` *(bool)*: Allow overwriting if `True`.
  - `verbose` *(bool)*: Print logs if `True`.

---

#### `move_files_to_parent(root_dir: str, levels_up=1, ext=None, verbose=False, safe_mode=True)`
Move files up to a parent folder.

- **Parameters**
  - `root_dir` *(str)*: Path to start.
  - `levels_up` *(int)*: Number of parent levels to move up.
  - `ext` *(str or None)*: File extension filter.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

### ❌ Deleting

#### `delete_files_by_extension(root_dir: str, ext: str, verbose=False, safe_mode=True)`
Delete all files of a given extension.

- **Parameters**
  - `root_dir` *(str)*: Path to scan.
  - `ext` *(str)*: Extension filter.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

#### `delete_folders_by_pattern(root_dir: str, pattern: str, verbose=False, safe_mode=True)`
Delete folders matching a regex pattern.

- **Parameters**
  - `root_dir` *(str)*: Path to scan.
  - `pattern` *(str)*: Regex for folder names.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

### 📦 Organizing

#### `organize_files_into_folders(root_dir: str, extension=".nii.gz", verbose=False, safe_mode=True)`
Move each file into its own folder named after the filename.

- **Parameters**
  - `root_dir` *(str)*: Path to scan.
  - `extension` *(str)*: File extension filter.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

#### `organize_subfolders_into_named_folders(root_dir: str, join_char="-", verbose=False, safe_mode=True)`
Flatten nested folder structures into combined names.

- **Parameters**
  - `root_dir` *(str)*: Path to scan.
  - `join_char` *(str)*: Separator between parent/subfolder names.
  - `verbose` *(bool)*: Print logs if `True`.
  - `safe_mode` *(bool)*: Simulate only if `True`.

---

### 📊 CSV & Dataset Handling

#### `concatenate_csv_files(path: str, output_file: str)`
Concatenate all CSV files in a directory into one.

- **Parameters**
  - `path` *(str)*: Directory with CSV files.
  - `output_file` *(str)*: Path of the output CSV file.

---

#### `read_datasets_from_dict(name_path_dict: dict, col_name="set") -> pd.DataFrame`
Load multiple CSV datasets into a single DataFrame.

- **Parameters**
  - `name_path_dict` *(dict)*: Keys = dataset names, values = CSV file paths.
  - `col_name` *(str)*: Column to hold dataset name. Default `"set"`.
- **Returns**
  - *(pd.DataFrame)*: Concatenated DataFrame with dataset labels.

---

## 🔎 Notes
- **Safe Mode**: Enabled by default to avoid unintended modifications.  
- **Verbose**: Useful for debugging file operations.  
- **Regex Support**: Available for folder deletion via `delete_folders_by_pattern`.
