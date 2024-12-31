import os
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import SimpleITK
from loguru import logger
from SimpleITK import GetArrayFromImage
from SimpleITK import GetImageFromArray
from SimpleITK import ReadImage
from SimpleITK import WriteImage


def load_nii(path_folder: str, as_array: bool = False) -> SimpleITK.Image:
    """  This function loads a NIfTI."""

    # Check if the file path exists
    if path_folder is None or not os.path.isfile(path_folder):
        raise ValueError(f"The file at {path_folder} does not exist or is not a valid file.")

    try:
        # Read the NIfTI file using SimpleITK
        image = ReadImage(str(path_folder))

        # Return as a numpy array if requested
        if as_array:
            return GetArrayFromImage(image)

        return image

    except RuntimeError as e:
        # Log specific errors related to SimpleITK
        logger.warning(f"Error loading NIfTI file {path_folder}: {e}")
        return None

    except Exception as e:
        # Catch other potential errors and raise a general error message
        logger.warning(f"Unexpected error while loading NIfTI file {path_folder}: {e}")
        return None


def load_nii_by_subject_id(root: str, subject_id: str, seq: str = "_seg", as_array: bool = False) -> SimpleITK.Image:
    """  This function loads a specific sequence from a NIfTI file by subject ID."""

    # Check if root or subject_id is None or empty
    if not root or not subject_id:
        raise ValueError("Invalid path or subject ID provided. Both must be non-empty strings.")

    nii_path = os.path.join(root, subject_id, f"{subject_id}{seq}.nii.gz")

    if not os.path.exists(nii_path):
        logger.warning(f"Sequence '{seq}' for subject '{subject_id}' not found at {nii_path}.")
        return None

    return load_nii(nii_path, as_array=as_array)


def read_sequences_dict(root: str, subject_id: str, sequences: Optional[List[str]] = None) -> dict:
    """
    Reads a dictionary of NIfTI sequences for a given subject from the specified root directory.

    Parameters:
        root (str): The root directory where subject data is stored.
        subject_id (str): The subject's ID used to locate the NIfTI files.
        sequences (List[str], optional): A list of sequences to load. Defaults to ["_t1", "_t1ce", "_t2", "_flair"].

    Returns:
        dict: A dictionary with sequence names (e.g., 't1', 't1ce', 't2', 'flair') as keys
              and Numpy arrays of the corresponding loaded NIfTI files or None if the sequence doesn't exist.
    """
    # Default sequences if none are provided
    if sequences is None:
        sequences = ["_t1", "_t1ce", "_t2", "_flair"]

    # Ensure root and subject_id are valid
    if not root or not subject_id:
        raise ValueError("Both 'root path' and 'subject id' must be non-empty strings.")

    out = {}
    for seq in sequences:
        nii_path = os.path.join(root, subject_id, f"{subject_id}{seq}.nii.gz")

        # Check if the NIfTI file exists
        if not os.path.isfile(nii_path):
            out[seq.replace("_", "")] = None
            logger.warning(f"Sequence '{seq}' for subject '{subject_id}' not found at {nii_path}.")
        else:
            try:
                # Attempt to load the sequence using load_nii
                out[seq.replace("_", "")] = load_nii(nii_path, as_array=True)
            except Exception as e:
                # Handle errors in loading the NIfTI file (e.g., corrupted file)
                out[seq.replace("_", "")] = None
                logger.error(f"Error loading sequence '{seq}' for subject '{subject_id}': {e}")

    return out


def get_spacing(img):
    if img is not None:
        return np.array(img.GetSpacing())
    else:
        logger.warning(f"Sequence empty. Assuming isotropic spacing (1, 1, 1).")
        return np.array([1, 1, 1])


def build_nifty_image(segmentation):
    """
    Converts a segmentation Numpy array into a SimpleITK Image.

    Parameters:
        segmentation (np.ndarray): The input segmentation as a Numpy array.

    Returns:
        SimpleITK.Image: The SimpleITK image created from the segmentation.

    Raises:
        ValueError: If the input is not a valid Numpy array.
    """
    if not isinstance(segmentation, (np.ndarray, list)):
        raise ValueError("The segmentation input must be a Numpy array or array-like object.")

    try:
        img = GetImageFromArray(segmentation)
        return img
    except Exception as e:
        raise RuntimeError(f"Error converting segmentation to NIfTI image: {e}")


def label_replacement(segmentation: np.array, original_labels: list, new_labels: list) -> np.array:
    """
    Maps the values in a segmentation array from original labels to desired new labels.

    Args:
        segmentation: The segmentation array containing the original label values.
        original_labels: A list of original labels present in the segmentation array.
        new_labels: A list of new labels that will replace the original labels.

    Returns:
        post_seg: A new segmentation array where the original labels have been mapped to the new labels.

    """
    if len(original_labels) != len(new_labels):
        raise ValueError("The lengths of original labels and new labels must match.")

    # Create a mapping dictionary from original labels to new labels
    mapping = {orig: new for orig, new in zip(original_labels, new_labels)}

    # Vectorized approach: Create a copy of the segmentation array
    post_seg = np.copy(segmentation)

    # Apply the mapping to the entire 3D array
    for orig, new in mapping.items():
        post_seg[segmentation == orig] = new

    return post_seg


def iterative_labels_replacement(
        root_dir: str,
        original_labels: list,
        new_labels: list,
        ext="_seg",
        verbose: bool = False
):
    """
    Iteratively replaces labels in segmentation files within a directory and its subdirectories.

    This function walks through all files in a specified root directory and its subdirectories,
    identifies files containing a specified extension (e.g., "_seg" or "_pred"), loads each file as a 3D image array,
    replaces the labels based on provided mappings, and saves the modified image back to its original location.

    Args:
        root_dir: The root directory containing the segmentation files.
        original_labels: A list of original labels present in the segmentation arrays.
        new_labels: A list of new labels that will replace the original labels.
        ext: The file extension pattern to identify segmentation files. Defaults to "_seg".
    """

    processed_files = 0
    skipped_files = 0

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            # Skip files that do not match the extension criteria
            if ext not in file:
                skipped_files += 1
                continue

            file_path = str(os.path.join(subdir, file))
            try:
                # Load the segmentation file as a 3D array
                seg = load_nii(file_path, as_array=True)

                # If segmentation data is None (e.g., file is corrupted), skip processing
                if seg is None:
                    logger.warning(f"Skipping file {file_path}: Unable to load segmentation.")
                    skipped_files += 1
                    continue

                # Perform label replacement
                post_seg = label_replacement(seg, original_labels, new_labels)

                # Save the modified segmentation array back to file
                WriteImage(build_nifty_image(post_seg), file_path)

                if verbose:
                    print(f"Processed file {file}")
                processed_files += 1

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                skipped_files += 1

    logger.info(f"Iterative label replacement completed: {processed_files} files processed, {skipped_files} files skipped.")


# def turn_planes(image, orientation=None):
#     """
#     Reorients the image planes based on the provided orientation.
#
#     Parameters:
#     ----------
#     orientation : list, optional
#         A list representing the desired plane orientations in order (default is ["axial", "coronal", "sagittal"]).
#
#     Returns:
#     -------
#     np.ndarray
#         The reoriented image array.
#     """
#
#     if not orientation:
#         orientation = ["axial", "coronal", "sagittal"]
#
#     # Get index position for each plane
#     axial = orientation.index("axial")
#     coronal = orientation.index("coronal")
#     sagittal = orientation.index("sagittal")
#
#     return np.transpose(image, (axial, coronal, sagittal))


def count_labels(segmentation, mapping_names=None):
    """
    Counts the number of pixels for each unique value in the segmentation.

    Returns:
    -------
    dict
        A dictionary with the counts of each unique value in the segmentation.
    """
    if segmentation is None:
        if mapping_names:
            return {k.lower(): np.nan for k in mapping_names.values()}
        else:
            return {}

    unique, counts = np.unique(segmentation, return_counts=True)
    pixels_dict = dict(zip(unique, counts))

    if mapping_names:
        pixels_dict = {mapping_names.get(k, k).lower(): v for k, v in pixels_dict.items()}

    return pixels_dict


def fit_brain_boundaries(sequence: np.ndarray, padding: int = 1):
    seq = sequence.copy()

    if np.all(seq == 0):
        return seq

    z_indexes, y_indexes, x_indexes = np.nonzero(seq != 0)

    zmin, ymin, xmin = np.min(z_indexes), np.min(y_indexes), np.min(x_indexes)
    zmax, ymax, xmax = np.max(z_indexes), np.max(y_indexes), np.max(x_indexes)

    zmin = max(0, zmin - padding)
    ymin = max(0, ymin - padding)
    xmin = max(0, xmin - padding)

    zmax = min(seq.shape[0] - 1, zmax + padding)
    ymax = min(seq.shape[1] - 1, ymax + padding)
    xmax = min(seq.shape[2] - 1, xmax + padding)

    seq = seq[zmin:zmax + 1, ymin:ymax + 1, xmin:xmax + 1]

    return seq
