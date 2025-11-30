import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import SimpleITK
from loguru import logger
from SimpleITK import GetArrayFromImage
from SimpleITK import GetImageFromArray
from SimpleITK import ReadImage
from SimpleITK import WriteImage


def load_nii(path: str, as_array: bool = False) -> Optional[Union[SimpleITK.Image, np.ndarray]]:
    """
    Load a NIfTI image from disk.

    This function reads a NIfTI file using SimpleITK. If ``as_array`` is True, the
    image is returned as a NumPy array; otherwise a ``SimpleITK.Image`` is returned.
    If an error occurs while reading, ``None`` is returned and a warning is logged.

    Parameters
    ----------
    path : str
        Path to the NIfTI file on disk (e.g., ``/path/to/scan.nii.gz``).
    as_array : bool, default False
        If True, return the image as a NumPy array; otherwise return a SimpleITK image.

    Returns
    -------
    Optional[Union[SimpleITK.Image, np.ndarray]]
        The loaded image (``SimpleITK.Image`` or ``np.ndarray``) if successful; otherwise ``None``.
    """
    if path is None or not os.path.isfile(path):
        raise ValueError(f"The file at {path} does not exist or is not a valid file.")

    try:
        image = ReadImage(str(path))
        if as_array:
            return GetArrayFromImage(image)
        return image
    except RuntimeError as e:
        logger.warning(f"Error loading NIfTI file {path}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error while loading NIfTI file {path}: {e}")
        return None


def load_nii_by_subject_id(
    root_dir: str, subject_id: str, seq: str = "_seg", as_array: bool = False
) -> Optional[Union[SimpleITK.Image, np.ndarray]]:
    """
    Load a specific NIfTI sequence for a subject ID from a dataset tree.

    This helper builds the expected path ``{root_dir}/{subject_id}/{subject_id}{seq}.nii.gz``,
    verifies its existence, and loads it via :func:`load_nii` optionally as a NumPy array.

    Parameters
    ----------
    root_dir : str
        Root folder containing all subject subfolders.
    subject_id : str
        Identifier of the subject (e.g., ``Patient-001``).
    seq : str, default "_seg"
        Sequence suffix to append to the subject id (e.g., "_t1", "_flair").
    as_array : bool, default False
        If True, return the image as a NumPy array; otherwise return a SimpleITK image.

    Returns
    -------
    Optional[Union[SimpleITK.Image, np.ndarray]]
        The loaded image if found and readable; otherwise ``None``.
    """
    if not root_dir or not subject_id:
        raise ValueError("Invalid path or subject ID provided. Both must be non-empty strings.")

    nii_path = os.path.join(root_dir, subject_id, f"{subject_id}{seq}.nii.gz")
    if not os.path.exists(nii_path):
        logger.warning(f"Sequence '{seq}' for subject '{subject_id}' not found at {nii_path}.")
        return None
    return load_nii(nii_path, as_array=as_array)


def read_sequences_dict(
    root_dir: str, subject_id: str, sequences: Optional[List[str]] = None
) -> Dict[str, Optional[np.ndarray]]:
    """
    Read multiple NIfTI sequences for a subject and return them as a dictionary.

    For each sequence in ``sequences`` (defaults to ``["_t1", "_t1ce", "_t2", "_flair"]``),
    attempts to load ``{subject_id}{seq}.nii.gz`` and returns a map from the sequence
    name without underscore (e.g., ``"t1"``) to a NumPy array. Missing or unreadable
    sequences are returned as ``None``.

    Parameters
    ----------
    root_dir : str
        Root directory where subject data is stored.
    subject_id : str
        Subject identifier used to locate the NIfTI files.
    sequences : list of str, optional
        Sequence suffixes to load. Defaults to ``["_t1", "_t1ce", "_t2", "_flair"]``.

    Returns
    -------
    dict[str, Optional[np.ndarray]]
        Mapping from sequence key (without leading underscore) to the loaded array,
        or ``None`` if the sequence file is missing/unreadable.
    """
    if sequences is None:
        sequences = ["_t1", "_t1ce", "_t2", "_flair"]
    if not root_dir or not subject_id:
        raise ValueError("Both 'root_dir path' and 'subject id' must be non-empty strings.")

    out = {}
    for seq in sequences:
        nii_path = os.path.join(root_dir, subject_id, f"{subject_id}{seq}.nii.gz")

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


def get_spacing(img: Optional[SimpleITK.Image]) -> np.ndarray:
    """
    Get voxel spacing of a SimpleITK image as a NumPy array.

    If ``img`` is ``None``, returns isotropic spacing ``[1, 1, 1]`` and logs a warning.

    Parameters
    ----------
    img : SimpleITK.Image or None
        Input image from which to read spacing.

    Returns
    -------
    np.ndarray
        The spacing vector as ``(z, y, x)``.
    """
    if img is not None:
        return np.array(img.GetSpacing())
    logger.warning("Sequence empty. Assuming isotropic spacing (1, 1, 1).")
    return np.array([1, 1, 1])


def build_nifty_image(segmentation: Union[np.ndarray, list]) -> SimpleITK.Image:
    """
    Convert a segmentation array into a SimpleITK Image.

    Parameters
    ----------
    segmentation : np.ndarray or list
        Input segmentation array.

    Returns
    -------
    SimpleITK.Image
        The created SimpleITK image.
    """
    if not isinstance(segmentation, (np.ndarray, list)):
        raise ValueError("The segmentation input must be a Numpy array or array-like object.")
    try:
        return GetImageFromArray(segmentation)
    except Exception as e:
        raise RuntimeError(f"Error converting segmentation to NIfTI image: {e}")


def label_replacement(segmentation: np.ndarray, original_labels: List[int], new_labels: List[int]) -> np.ndarray:
    """
    Map label values in a segmentation from original labels to new labels.

    Parameters
    ----------
    segmentation : np.ndarray
        Segmentation array containing the original label values.
    original_labels : list of int
        Original labels present in the segmentation array.
    new_labels : list of int
        New labels to replace the original labels.

    Returns
    -------
    np.ndarray
        A new segmentation array with the remapped labels.
    """
    if len(original_labels) != len(new_labels):
        raise ValueError("The lengths of original labels and new labels must match.")
    mapping = {orig: new for orig, new in zip(original_labels, new_labels)}
    post_seg = np.copy(segmentation)
    for orig, new in mapping.items():
        post_seg[segmentation == orig] = new
    return post_seg


def iterative_labels_replacement(
    root_dir: str, original_labels: List[int], new_labels: List[int], ext: str = "_seg", verbose: bool = False
):
    """
    Iteratively replace labels in segmentation files across a dataset tree.

    Walks the directory tree ``root_dir``, finds files whose names contain ``ext``
    (e.g., "_seg" or "_pred"), loads each file as a 3D array, replaces labels
    using :func:`label_replacement`, and writes the modified segmentation back in place.

    Parameters
    ----------
    root_dir : str
        Root directory containing segmentation files.
    original_labels : list of int
        Original label values present in the segmentation arrays.
    new_labels : list of int
        New labels that will replace the original labels.
    ext : str, default "_seg"
        File-name pattern used to identify segmentation files.
    verbose : bool, default False
        If True, log per-file processing details.
    """

    processed_files = 0
    skipped_files = 0

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if ext not in file:
                skipped_files += 1
                continue

            file_path = str(os.path.join(subdir, file))
            try:
                seg = load_nii(file_path, as_array=True)
                if seg is None:
                    logger.warning(f"Skipping file {file_path}: Unable to load segmentation.")
                    skipped_files += 1
                    continue

                post_seg = label_replacement(seg, original_labels, new_labels)
                WriteImage(build_nifty_image(post_seg), file_path)

                if verbose:
                    print(f"Processed file {file}")
                processed_files += 1

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                skipped_files += 1

    logger.info(
        f"Iterative label replacement completed: {processed_files} files processed, {skipped_files} files skipped."
    )


def count_labels(
    segmentation: Optional[np.ndarray], mapping_names: Optional[Dict[int, str]] = None
) -> Dict[Union[int, str], float]:
    """
    Count the number of pixels/voxels for each unique value in a segmentation.

    If ``segmentation`` is ``None``, return an empty dict, or a dict with NaN values
    for keys provided by ``mapping_names``.

    Parameters
    ----------
    segmentation : np.ndarray or None
        Segmentation array to count values from.
    mapping_names : dict[int, str], optional
        Mapping to rename label IDs (keys) to friendly names (values).

    Returns
    -------
    dict[Union[int, str], float]
        Counts per unique label (renamed if ``mapping_names`` is provided).
    """
    if segmentation is None:
        if mapping_names:
            return {k.lower(): np.nan for k in mapping_names.values()}  # type: ignore[return-value]
        return {}

    unique, counts = np.unique(segmentation, return_counts=True)
    pixels_dict = dict(zip(unique, counts))

    if mapping_names:
        pixels_dict = {mapping_names.get(k, k).lower(): v for k, v in pixels_dict.items()}

    return pixels_dict


def fit_brain_boundaries(sequence: np.ndarray, padding: int = 1) -> np.ndarray:
    """
    Crop a 3D sequence tightly around the non-zero brain region with optional padding.

    The function computes the bounding box around non-zero voxels and returns the
    cropped subvolume. If the input is all zeros, the input is returned unchanged.

    Parameters
    ----------
    sequence : np.ndarray
        Input 3D array to crop.
    padding : int, default 1
        Number of voxels to pad the bounding box on each side.

    Returns
    -------
    np.ndarray
        Cropped subvolume of ``sequence``.
    """
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

    seq = seq[zmin : zmax + 1, ymin : ymax + 1, xmin : xmax + 1]

    return seq
