import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import SimpleITK
from loguru import logger

from audit.io.readers import ImageData
from audit.io.readers import get_reader
from audit.io.readers import infer_format
from audit.io.readers import read_subject_image
from audit.utils.modalities.base import ModalityBase


class USModality(ModalityBase):
    """
    Ultrasound (US) Modality implementation.
    Handles loading and managing 2D US images stored in formats like PNG or JPEG.
    """

    def load_sequence(
        self, path: str, as_array: bool = False, format_name: Optional[str] = None
    ) -> Optional[Union[SimpleITK.Image, np.ndarray]]:
        """
        Load a 2D US image from disk.
        Supports common 2D formats (.png, .jpg, etc.).
        """
        if path is None:
            raise ValueError("A non-empty image path is required.")
        data = get_reader(format_name or infer_format(path)).read(path)
        return data.array if as_array else data.image

    def read_sequences_dict(
        self,
        root_dir: str,
        subject_id: str,
        sequences: Optional[List[str]] = None,
        format_name: Optional[str] = None,
        reader_options: Optional[dict] = None,
    ) -> Dict[str, Optional[np.ndarray]]:
        """
        Read one or more US sequences using the configured subject naming
        convention. With no sequences, the image is ``<subject>/<subject>.<ext>``.
        """
        return {
            key: data.array if data is not None else None
            for key, data in self.read_sequence_data_dict(
                root_dir, subject_id, sequences, format_name, reader_options
            ).items()
        }

    def read_sequence_data_dict(
        self,
        root_dir: str,
        subject_id: str,
        sequences: Optional[List[str]] = None,
        format_name: Optional[str] = None,
        reader_options: Optional[dict] = None,
    ) -> Dict[str, Optional[ImageData]]:
        out = {}
        subject_dir = os.path.join(root_dir, subject_id)

        if not sequences:
            try:
                out["default"] = read_subject_image(
                    root_dir,
                    subject_id,
                    "",
                    format_name or self.get_default_format(),
                    **(reader_options or {}),
                )
            except FileNotFoundError:
                logger.warning(f"No valid US images found dynamically for subject '{subject_id}' at {subject_dir}.")
                out["default"] = None
        else:
            for seq in sequences:
                seq_key = seq.replace("_", "")
                try:
                    out[seq_key] = read_subject_image(
                        root_dir,
                        subject_id,
                        seq,
                        format_name or self.get_default_format(),
                        **(reader_options or {}),
                    )
                except FileNotFoundError:
                    logger.warning(f"Sequence '{seq}' for US subject '{subject_id}' not found in any common format.")
                    out[seq_key] = None

        return out

    def get_spacing(self, img: Optional[SimpleITK.Image]) -> np.ndarray:
        """
        Get pixel spacing in NumPy axis order. US is usually 2D.
        """
        if img is not None:
            return np.asarray(img.GetSpacing(), dtype=float)[::-1]

        logger.warning("Sequence empty or invalid. Assuming isotropic 2D spacing (1, 1).")
        return np.ones(2)

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

    def get_default_format(self) -> str:
        return "auto"
