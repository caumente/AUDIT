[//]: # (::: src.utils.sequences)

The `utils.sequences` module provides a set of utilities for handling 3D medical imaging data in the NIfTI format. This module includes functions for loading NIfTI files, processing segmentation data, replacing labels, and extracting features from medical image sequences.

### Overview

The `sequences` module focuses on simplifying the handling and processing of 3D medical images. It includes functions for tasks such as:

- Loading NIfTI files either as `SimpleITK.Image` objects or as NumPy arrays.
- Replacing labels in segmentation data with desired mappings.
- Iteratively processing segmentation files within a directory.
- Extracting image dimensions, voxel spacing, and label counts.
- Fitting boundaries around non-zero regions of medical images.

These utilities are designed for streamlined medical image processing workflows.

### Methods

#### `load_nii()`

**Description**:  
Loads a NIfTI file from the specified path and returns it as a `SimpleITK.Image` object or a NumPy array.

**Parameters**:
- `path_folder` (`str`): The file path to the NIfTI file.
- `as_array` (`bool`, optional): If `True`, returns the NIfTI file as a NumPy array. Defaults to `False`.

**Returns**:
- `SimpleITK.Image` or `np.ndarray`: The loaded NIfTI file.

**Exceptions**:
- Raises `ValueError` if the file path is invalid.
- Logs warnings for errors during file loading.

----------------------------  

#### `load_nii_by_subject_id()`

**Description**:  
Loads a specific sequence from a NIfTI file using the subject ID and sequence identifier.

**Parameters**:
- `root` (`str`): The root directory containing subject data.
- `subject_id` (`str`): The subject's ID.
- `seq` (`str`, optional): The sequence identifier (e.g., "_seg"). Defaults to "_seg".
- `as_array` (`bool`, optional): If `True`, returns the NIfTI file as a NumPy array. Defaults to `False`.

**Returns**:
- `SimpleITK.Image` or `np.ndarray`: The loaded NIfTI file.

**Notes**:
- Logs warnings if the sequence is not found.

----------------------------  

#### `read_sequences_dict()`

**Description**:  
Reads a dictionary of NIfTI sequences for a subject from the specified directory.

**Parameters**:
- `root` (`str`): The root directory containing subject data.
- `subject_id` (`str`): The subject's ID.
- `sequences` (`List[str]`, optional): A list of sequence identifiers to load (e.g., `["_t1", "_t1ce", "_t2", "_flair"]`). Defaults to these four sequences.

**Returns**:
- `dict`: A dictionary with sequence names as keys and the corresponding NIfTI files or `None` if a sequence is not found.

----------------------------  

#### `get_spacing()`

**Description**:  
Extracts the voxel spacing from a `SimpleITK.Image`.

**Parameters**:
- `img` (`SimpleITK.Image`): The input image.

**Returns**:
- `np.ndarray`: The voxel spacing. Defaults to `[1, 1, 1]` if the image is empty.

----------------------------  

#### `build_nifty_image()`

**Description**:  
Converts a segmentation NumPy array into a `SimpleITK.Image`.

**Parameters**:
- `segmentation` (`np.ndarray`): The input segmentation array.

**Returns**:
- `SimpleITK.Image`: The converted image.

**Exceptions**:
- Raises `ValueError` for invalid inputs.

----------------------------  

#### `label_replacement()`

**Description**:  
Maps original labels in a segmentation array to new labels.

**Parameters**:
- `segmentation` (`np.ndarray`): The input segmentation array.
- `original_labels` (`list`): List of original labels.
- `new_labels` (`list`): List of new labels.

**Returns**:
- `np.ndarray`: The segmentation array with labels replaced.

**Exceptions**:
- Raises `ValueError` if the lengths of the label lists do not match.

----------------------------  

#### `iterative_labels_replacement()`

**Description**:  
Iteratively replaces labels in segmentation files within a directory.

**Parameters**:
- `root_dir` (`str`): The root directory containing segmentation files.
- `original_labels` (`list`): List of original labels.
- `new_labels` (`list`): List of new labels.
- `ext` (`str`, optional): File extension to identify segmentation files. Defaults to "_seg".
- `verbose` (`bool`, optional): If `True`, prints progress. Defaults to `False`.

**Notes**:
- Logs the number of files processed and skipped.

----------------------------  

#### `count_labels()`

**Description**:  
Counts the number of pixels for each unique label in a segmentation.

**Parameters**:
- `segmentation` (`np.ndarray`): The input segmentation array.
- `mapping_names` (`dict`, optional): A mapping of label values to names.

**Returns**:
- `dict`: A dictionary with label counts.

----------------------------  

#### `fit_brain_boundaries()`

**Description**:  
Fits boundaries around the non-zero regions of a 3D medical image with optional padding.

**Parameters**:
- `sequence` (`np.ndarray`): The input 3D image.
- `padding` (`int`, optional): The amount of padding to add around the boundaries. Defaults to `1`.

**Returns**:
- `np.ndarray`: The cropped 3D image with boundaries fitted around the non-zero regions.

----------------------------  
