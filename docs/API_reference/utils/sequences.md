
The `sequences` module provides helpers for loading, manipulating, and analyzing NIfTI images and segmentations.

!!! warning "Important"
    Some of the functions presented in this module are used internally by **AUDIT** and are not intended to be used
    by users.

---

## __I/O Operations__

### `load_nii`

Load a NIfTI image from disk.

This function reads a NIfTI file using SimpleITK. If `as_array` is True, the
image is returned as a NumPy array; otherwise a `SimpleITK.Image` is returned.
If an error occurs while reading, `None` is returned and a warning is logged.

**Parameters**  

- **path_folder** (`str`): Path to the NIfTI file on disk (e.g., `/path/to/scan.nii.gz`).  
- **as_array** (`bool`, default: `False`): If True, return the image as a NumPy array; otherwise return a SimpleITK image.

**Returns**  

- `SimpleITK.Image | np.ndarray | None`: The loaded image (`SimpleITK.Image` or `np.ndarray`) if successful; otherwise `None`.

---

### `load_nii_by_subject_id`

Load a specific NIfTI sequence for a subject ID from a dataset tree.

This helper builds the expected path `{root_dir}/{subject_id}/{subject_id}{seq}.nii.gz`, 
verifies its existence, and loads it via `load_nii` optionally as a NumPy array.

**Parameters**  

- **root_dir** (`str`): Root folder containing all subject subfolders.  
- **subject_id** (`str`): Identifier of the subject (e.g., `Patient-001`).  
- **seq** (`str`, default: `"_seg"`): Sequence suffix to append to the subject id (e.g., `_t1`, `_flair`).  
- **as_array** (`bool`, default: `False`): If True, return the image as a NumPy array; otherwise return a SimpleITK image.

**Returns**  

- `SimpleITK.Image | np.ndarray | None`: The loaded image if found and readable; otherwise `None`.

---

## __Reading Multiple Sequences__

### `read_sequences_dict`

Read multiple NIfTI sequences for a subject and return them as a dictionary.

For each sequence in `sequences` (defaults to `["_t1", "_t1ce", "_t2", "_flair"]`),
attempts to load `{subject_id}{seq}.nii.gz` and returns a map from the sequence
name without underscore (e.g., `"t1"`) to a NumPy array. Missing or unreadable
sequences are returned as `None`.

**Parameters**  

- **root_dir** (`str`): Root directory where subject data is stored.  
- **subject_id** (`str`): Subject identifier used to locate the NIfTI files.  
- **sequences** (`list[str]`, optional): Sequence suffixes to load. Defaults to `["_t1", "_t1ce", "_t2", "_flair"]`.

**Returns**  

- `dict[str, np.ndarray | None]`: Mapping from sequence key (without leading underscore) to the loaded array, or `None` if missing/unreadable.

---

## __Spacing & Conversion__

### `get_spacing`

Get voxel spacing of a SimpleITK image as a NumPy array.

If `img` is `None`, returns isotropic spacing `[1, 1, 1]` and logs a warning.

**Parameters**  

- **img** (`SimpleITK.Image | None`): Input image from which to read spacing.

**Returns**  

- `np.ndarray`: The spacing vector as `(z, y, x)`.

---

### `build_nifty_image`

Convert a segmentation array into a SimpleITK Image.

**Parameters**  

- **segmentation** (`np.ndarray | list`): Input segmentation array.

**Returns**  

- `SimpleITK.Image`: The created SimpleITK image.

---

## __Label Operations__

### `label_replacement`

Map label values in a segmentation from original labels to new labels.

**Parameters**  

- **segmentation** (`np.ndarray`): Segmentation array containing the original label values.  
- **original_labels** (`list[int]`): Original labels present in the segmentation array.  
- **new_labels** (`list[int]`): New labels to replace the original labels.

**Returns**  

- `np.ndarray`: A new segmentation array with the remapped labels.

---

### `iterative_labels_replacement`

Iteratively replace labels in segmentation files across a dataset tree.

Walks the directory tree `root_dir`, finds files whose names contain `ext`
(e.g., `_seg` or `_pred`), loads each file as a 3D array, replaces labels
using `label_replacement`, and writes the modified segmentation back in place.

**Parameters**  

- **root_dir** (`str`): Root directory containing segmentation files.  
- **original_labels** (`list[int]`): Original label values present in the segmentation arrays.  
- **new_labels** (`list[int]`): New labels that will replace the original labels.  
- **ext** (`str`, default: `"_seg"`): File-name pattern used to identify segmentation files.  
- **verbose** (`bool`, default: `False`): If True, log per-file processing details.

---

## __Analysis Utilities__

### `count_labels`

Count the number of pixels/voxels for each unique value in a segmentation.

If `segmentation` is `None`, return an empty dict, or a dict with NaN values
for keys provided by `mapping_names`.

**Parameters**  

- **segmentation** (`np.ndarray | None`): Segmentation array to count values from.  
- **mapping_names** (`dict[int, str]`, optional): Mapping to rename label IDs (keys) to friendly names (values).

**Returns**  

- `dict[int | str, float]`: Counts per unique label (renamed if `mapping_names` is provided).

---

### `fit_brain_boundaries`

Crop a 3D sequence tightly around the non-zero brain region with optional padding.

The function computes the bounding box around non-zero voxels and returns the
cropped subvolume. If the input is all zeros, the input is returned unchanged.

**Parameters**  

- **sequence** (`np.ndarray`): Input 3D array to crop.  
- **padding** (`int`, default: `1`): Number of voxels to pad the bounding box on each side.

**Returns**  

- `np.ndarray`: Cropped subvolume of `sequence`.