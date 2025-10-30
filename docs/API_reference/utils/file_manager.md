The `file_manager` module provides a comprehensive set of utilities for managing files and directories. It supports operations for listing, renaming, copying, moving, deleting, and organizing files, with pattern matching, recursion, and safe simulation modes.

---

## __Project Initialization__

### `create_project_structure`

Creates the project directory structure and copies default config files
from the installed __AUDIT__ package into the project's configs folder.


```text
your_project/
├── datasets/
├── configs/
│   ├── app.yaml
│   ├── feature_extraction.yaml
│   └── metric_extraction.yaml
├── outputs/
└── logs/
```

**Parameters**  

- **base_path** (`str`, default: `"./"`): Root directory name where the project structure will be created.


---

## __Listing Operations__

### `list_dirs`

List directories in a given path.

**Parameters**  

- **path** (`str` or `Path`): The root directory where to look for subdirectories.  
- **recursive** (`bool`, default: `False`): If True, search subdirectories recursively.  
- **full_path** (`bool`, default: `False`): If True, return absolute paths instead of just directory names.  
- **pattern** (`str`, optional): Optional regex pattern to filter directory names.

**Returns**  

- `list[str]`: A sorted list of directory names or paths.


---

### `list_files`

List files in a given directory.

**Parameters**  

- **path** (`str` or `Path`): Root directory to search.  
- **recursive** (`bool`, default: `False`): If True, search subdirectories recursively.  
- **full_path** (`bool`, default: `False`): If True, return absolute paths instead of just filenames.  
- **pattern** (`str`, optional): Regex pattern to filter file names.  
- **extensions** (`list[str]` or `None`, optional): List of file extensions to filter by (e.g., `['.csv', '.yml']`).

**Returns**  

- `list[str]`: A sorted list of file names or paths.


---

## __Directory Operations__

### `rename_dirs`

Rename directories recursively by replacing a substring in their names.

**Parameters**  

- **root_dir** (`str` or `Path`): Path to the directory where renaming will be performed.  
- **old_name** (`str`): The string to be replaced in the directory names.  
- **new_name** (`str`): The new string that will replace old_name.  
- **verbose** (`bool`, default: `False`): If True, print information about each rename operation.  
- **safe_mode** (`bool`, default: `True`): If True, only simulate renaming without making changes.


---

### `add_string_dirs`

Add a prefix and/or suffix to all directories and subdirectories.

**Parameters**  

- **root_dir** (`str` or `Path`): Root directory to start renaming.  
- **prefix** (`str`, default: `""`): Prefix to add to directory names.  
- **suffix** (`str`, default: `""`): Suffix to add to directory names.  
- **verbose** (`bool`, default: `False`): If True, print information about renamed directories (only when safe_mode=False).  
- **safe_mode** (`bool`, default: `True`): If True, simulate renaming without changing directories.


---

## __File Operations__

### `rename_files`

Recursively rename files by replacing a substring in their filenames.

**Parameters**  

- **root_dir** (`str` or `Path`): Root directory to start renaming files.  
- **old_name** (`str`, default: `""`): Substring in filenames to replace.  
- **new_name** (`str`, default: `""`): Substring to replace old_name with.  
- **verbose** (`bool`, default: `False`): If True, print information about renamed files (only when safe_mode=False).  
- **safe_mode** (`bool`, default: `True`): If True, simulate renaming without changing files.


---

### `add_suffix_to_files`

Adds a suffix to all files with a specific extension in a folder and its subdirectories.

**Parameters**  

- **root_dir** (`str`): The folder where the files are located.  
- **suffix** (`str`, default: `"_pred"`): The suffix to add to the filenames before the extension.  
- **ext** (`str`, default: `".nii.gz"`): The file extension to search for and rename.  
- **verbose** (`bool`, default: `False`): If True, print detailed information about each file being renamed.  
- **safe_mode** (`bool`, default: `True`): If True, simulate the renaming operation without changing any files.


---

### `add_string_files`

Add a prefix and/or suffix to all files in a folder and its subfolders.

**Parameters**  

- **root_dir** (`str` or `Path`): Directory containing files to rename.  
- **prefix** (`str`, default: `""`): Prefix to add to the file name (before the stem).  
- **suffix** (`str`, default: `""`): Suffix to add to the file name (after the stem, before extension).  
- **ext** (`str` or `None`, optional): If provided, treat this exact string as the file extension (supports multi-part extensions like `'.nii.gz'`).  
- **verbose** (`bool`, default: `False`): If True, print information about actual renames (only when safe_mode=False).  
- **safe_mode** (`bool`, default: `True`): If True, simulate renames and print planned operations (no filesystem changes).


---

## __Copying and Moving Operations__

### `copy_files_by_extension`

Copy all files with a specific extension from one directory to another.

**Parameters**  

- **src_dir** (`str`): The source directory from which to copy files.  
- **dst_dir** (`str`): The destination directory where files will be copied.  
- **ext** (`str`): The file extension to search for and copy (e.g., `".txt"`, `".yaml"`).  
- **safe_mode** (`bool`, default: `True`): If True, simulate the operation without making changes.  
- **overwrite** (`bool`, default: `False`): If True, allow overwriting existing files in the destination directory.  
- **verbose** (`bool`, default: `False`): If True, print detailed logs for each file operation.


---

### `move_files_to_parent`

Move files (optionally filtered by extension) from subdirectories
to a specified parent level above their current location.

**Parameters**  

- **root_dir** (`str`): Root directory where the search will start.  
- **levels_up** (`int`, default: `1`): Number of parent levels up to move the files.  
- **ext** (`str` or `None`, optional): File extension to filter by (e.g., `".txt"`).  
- **verbose** (`bool`, default: `False`): If True, print detailed logs for each file move operation.  
- **safe_mode** (`bool`, default: `True`): If True, simulate the move without actually moving the files.


---

## __Deletion Operations__

### `delete_files_by_extension`

Deletes all files with a specific extension in a path and its subdirectories.

**Parameters**  

- **root_dir** (`str`): The root directory where the search will start.  
- **ext** (`str`): The file extension of the files to be deleted (e.g., `'.nii.gz'`).  
- **verbose** (`bool`, default: `False`): If True, print detailed logs for each file deletion operation.  
- **safe_mode** (`bool`, default: `True`): If True, simulate the deletion without actually removing the files.


---

### `delete_dirs_by_pattern`

Deletes folders matching a pattern in a path and its subdirectories.

**Parameters**  

- **root_dir** (`str`): Directory where the search will start.  
- **pattern** (`str`): Pattern to match folder names.  
- **match_type** (`str`, default: `'contains'`): Type of matching: `'contains'`, `'starts'`, `'ends'`, or `'exact'`.  
- **verbose** (`bool`, default: `False`): If True, print detailed logs for each folder deletion operation.  
- **safe_mode** (`bool`, default: `True`): If True, simulate deletion without actually removing folders.


---

## __Organization Operations__

### `organize_files_into_dirs`

Organizes files into folders based on their filenames. Each file will be moved into a folder named
after the file (excluding the extension).

**Parameters**  

- **root_dir** (`str`): Directory containing the files to organize.  
- **extension** (`str`, default: `'.nii.gz'`): The file extension to look for.  
- **verbose** (`bool`, default: `False`): If True, print detailed logs about each file being organized.  
- **safe_mode** (`bool`, default: `True`): If True, simulate the file organization without moving the files.


---

### `organize_subdirs_into_named_dirs`

Organizes subfolders into combined named folders.
Combines parent folder names and their subfolder names into a single folder per subfolder.

**Parameters**  

- **root_dir** (`str`): Directory containing the parent folders.  
- **join_char** (`str`, default: `"-"`): Character to join parent and subfolder names.  
- **verbose** (`bool`, default: `False`): If True, print detailed logs about each operation.  
- **safe_mode** (`bool`, default: `True`): If True, simulate the folder organization without making changes.

**Returns**  

- `dict[str, list[str]]`: Summary of operations performed or simulated.  
  Keys: `"created_folders"`, `"moved_items"`, `"removed_folders"`.
