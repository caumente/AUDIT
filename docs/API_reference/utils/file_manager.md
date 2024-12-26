[//]: # (::: src.utils.operations.file_operations)

The `file_operations` module provides utilities for managing directories, reading and writing data files, and handling CSV and JSON file formats. These utilities are designed to streamline common file I/O operations.

### Overview

The `file_operations` module includes functions for:

- Creating directories if they do not exist.
- Reading and writing JSON and CSV files.
- Managing files and directories.

These utilities are aimed at simplifying file management tasks using AUDIT library.

### Methods

#### `ensure_dir()`

**Description**:  
Ensures that a directory exists, creating it if necessary.

**Parameters**:
- `path` (`str`): The path to the directory.

**Returns**:  
None.

**Notes**:  
Logs the creation of the directory.

----------------------------  

#### `read_json()`

**Description**:  
Reads a JSON file and returns its content.

**Parameters**:
- `path` (`str`): The path to the JSON file.

**Returns**:
- `dict`: The content of the JSON file.

**Exceptions**:  
- Raises `FileNotFoundError` if the file does not exist.  
- Raises `JSONDecodeError` for invalid JSON.

----------------------------  

#### `write_json()`

**Description**:  
Writes a dictionary to a JSON file.

**Parameters**:
- `data` (`dict`): The data to write to the file.
- `path` (`str`): The path to the output JSON file.

**Returns**:  
None.

**Exceptions**:  
- Raises `TypeError` if the data is not serializable.

----------------------------  

#### `read_csv()`

**Description**:  
Reads a CSV file and returns its content as a pandas DataFrame.

**Parameters**:
- `path` (`str`): The path to the CSV file.

**Returns**:
- `pd.DataFrame`: The content of the CSV file.

**Exceptions**:  
- Raises `FileNotFoundError` if the file does not exist.  
- Raises `pd.errors.ParserError` for malformed CSV.

----------------------------  

#### `write_csv()`

**Description**:  
Writes a pandas DataFrame to a CSV file.

**Parameters**:
- `data` (`pd.DataFrame`): The DataFrame to write to the file.
- `path` (`str`): The path to the output CSV file.

**Returns**:  
None.

**Exceptions**:  
- Raises `ValueError` if the data is not a valid DataFrame.

----------------------------  

#### `log_operation()`

**Description**:  
Logs details of file operations, such as reads, writes, and errors.

**Parameters**:
- `message` (`str`): The log message.
- `log_file` (`str`, optional): Path to the log file. Defaults to `"operations.log"`.

**Returns**:  
None.

**Notes**:  
Appends log messages to the specified file.

