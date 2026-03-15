import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import SimpleITK
from loguru import logger
from PIL import Image

from audit.utils.modalities.base import ModalityBase


class USModality(ModalityBase):
    """
    Ultrasound (US) Modality implementation.
    Handles loading and managing 2D US images stored in formats like PNG or JPEG.
    """

    def load_sequence(self, path: str, as_array: bool = False) -> Optional[Union[SimpleITK.Image, np.ndarray]]:
        """
        Load a 2D US image from disk.
        Supports common 2D formats (.png, .jpg, etc.).
        """
        if path is None or not os.path.isfile(path):
            raise ValueError(f"The file at {path} does not exist or is not a valid file.")

        try:
            # We first try SimpleITK
            image = SimpleITK.ReadImage(str(path))

            # If the image has >1 channels (e.g. RGB) and we need a single channel:
            if image.GetNumberOfComponentsPerPixel() > 1:
                # Convert to grayscale
                logger.debug(f"Converting RGB US image to grayscale for path: {path}")
                cast_filter = SimpleITK.VectorIndexSelectionCastImageFilter()
                cast_filter.SetIndex(0)  # Keep first channel as proxy for grayscale for now.
                image = cast_filter.Execute(image)

            if as_array:
                arr = SimpleITK.GetArrayFromImage(image)
                # Ensure we represent this correctly, typically SimpleITK loads 2D as (Y, X)
                return arr
            return image
        except RuntimeError as e:
            logger.warning(f"SimpleITK failed to load US file {path}: {e}. Falling back to PIL.")
            try:
                # Fallback to PIL
                pil_img = Image.open(path).convert("L")  # Force grayscale
                arr = np.array(pil_img)
                if as_array:
                    return arr
                else:
                    return SimpleITK.GetImageFromArray(arr)
            except Exception as e2:
                logger.error(f"Fallback PIL error while loading US file {path}: {e2}")
                return None
        except Exception as e:
            logger.warning(f"Unexpected error while loading US file {path}: {e}")
            return None

    def read_sequences_dict(
        self, root_dir: str, subject_id: str, sequences: Optional[List[str]] = None
    ) -> Dict[str, Optional[np.ndarray]]:
        """
        Read multiple (or single) sequence for an US subject.
        Since US might just be purely one image, if sequences are given, it tries them.
        If not, it just tries to load the first valid 2D image file it finds in the subject directory.
        """
        out = {}
        subject_dir = os.path.join(root_dir, subject_id)

        if not sequences:
            # Look for common 2D formats
            # This is a fallback behavior for single-sequence 2D modalities
            valid_exts = [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]
            found_img = None
            if os.path.isdir(subject_dir):
                for file in os.listdir(subject_dir):
                    if any(file.lower().endswith(ext) for ext in valid_exts):
                        if "_seg" not in file.lower() and "_pred" not in file.lower():
                            found_img = os.path.join(subject_dir, file)
                            break

            if found_img:
                logger.info(f"Dynamically discovered US image for {subject_id}: {found_img}")
                out["default"] = self.load_sequence(found_img, as_array=True)
            else:
                logger.warning(f"No valid US images found dynamically for subject '{subject_id}' at {subject_dir}.")
                out["default"] = None
        else:
            # If explicit sequences are provided (e.g. ['_bmode', '_doppler'])
            valid_exts = [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".dcm", ".mha", ".nrrd"]
            for seq in sequences:
                seq_key = seq.replace("_", "")
                found = False
                for ext in valid_exts:
                    img_path = os.path.join(subject_dir, f"{subject_id}{seq}{ext}")
                    if os.path.isfile(img_path):
                        out[seq_key] = self.load_sequence(img_path, as_array=True)
                        found = True
                        break

                if not found:
                    logger.warning(f"Sequence '{seq}' for US subject '{subject_id}' not found in any common format.")
                    out[seq_key] = None

        return out

    def get_spacing(self, img: Optional[SimpleITK.Image]) -> np.ndarray:
        """
        Get pixel spacing of a SimpleITK image. US is usually 2D.
        Returns a 3-element vector (Z, Y, X) for compatibility with MRI (Z=1).
        """
        if img is not None:
            spacing = list(img.GetSpacing())  # Typically (X, Y) for 2D
            if len(spacing) == 2:
                return np.array([1.0, spacing[1], spacing[0]])  # (Z, Y, X)
            elif len(spacing) >= 3:
                return np.array([spacing[2], spacing[1], spacing[0]])

        logger.warning("Sequence empty or invalid. Assuming isotropic spacing 2D/3D (1, 1, 1).")
        return np.array([1.0, 1.0, 1.0])

    def build_image(self, segmentation: Union[np.ndarray, list]) -> SimpleITK.Image:
        """
        Convert a segmentation array into a SimpleITK Image.
        """
        if not isinstance(segmentation, (np.ndarray, list)):
            raise ValueError("The segmentation input must be a Numpy array or array-like object.")
        try:
            return SimpleITK.GetImageFromArray(segmentation)
        except Exception as e:
            raise RuntimeError(f"Error converting segmentation to SimpleITK image: {e}")

    def preprocess(self, sequence: np.ndarray, **kwargs) -> np.ndarray:
        """
        US-specific preprocessing.
        Applies basic speckle reduction or normalization if configured.
        """
        # Feature placeholder: Could add median filter or anisotropic diffusion here for US.
        # For now, return as is, acting transparently unless kwargs command action.
        seq = np.copy(sequence).astype(np.float32)

        # Simple Min-Max Normalization which is very common in US
        if kwargs.get("normalize", False):
            seq_min = np.min(seq)
            seq_max = np.max(seq)
            if seq_max - seq_min > 0:
                seq = (seq - seq_min) / (seq_max - seq_min)

        return seq

    def run_comparison_segmentation_viewer(
        self, path_seg: str, path_pred: str, case: str, labels: Optional[Dict] = None
    ) -> bool:
        """
        US images usually don't need ITK-Snap unless converted to NIfTI proxy.
        For now, we warn and bypass since we assume 2D PNG/JPEG.
        """
        logger.warning("ITK-SNAP comparison not supported out-of-the-box for raw 2D US images yet.")
        return False

    def get_default_sequences(self) -> List[str]:
        """
        Returns an empty list as US typically relies on single images without sequence names.
        """
        return []
