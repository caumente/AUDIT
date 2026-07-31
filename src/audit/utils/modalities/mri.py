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
from audit.utils.external_tools.itk_snap import run_comparison_segmentation_itk_snap as legacy_itk_snap
from audit.utils.modalities.base import ModalityBase
from audit.utils.sequences.sequences import build_nifty_image as legacy_build_nifty_image


class MRIModality(ModalityBase):
    """
    MRI Modality implementation.
    Wraps existing MRI logic from sequences.py and itk_snap.py.
    """

    def load_sequence(
        self, path: str, as_array: bool = False, format_name: Optional[str] = None
    ) -> Optional[Union[SimpleITK.Image, np.ndarray]]:
        """
        Load an MRI image from any registered storage format.
        """
        reader = get_reader(format_name or infer_format(path))
        data = reader.read(path)
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
        Read multiple NIfTI sequences for an MRI subject.
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
        sequences = self.get_default_sequences() if sequences is None else sequences
        output = {}
        for sequence in sequences:
            key = sequence.replace("_", "")
            try:
                output[key] = read_subject_image(
                    root_dir,
                    subject_id,
                    sequence,
                    format_name or self.get_default_format(),
                    **(reader_options or {}),
                )
            except FileNotFoundError:
                logger.warning(f"Sequence '{sequence}' for MRI subject '{subject_id}' was not found.")
                output[key] = None
        return output

    def get_spacing(self, img: Optional[SimpleITK.Image]) -> np.ndarray:
        """
        Get voxel spacing in NumPy axis order.
        """
        if img is None:
            logger.warning("Sequence empty. Assuming isotropic spacing (1, 1, 1).")
            return np.ones(3)
        return np.asarray(img.GetSpacing(), dtype=float)[::-1]

    def build_image(self, segmentation: Union[np.ndarray, list]) -> SimpleITK.Image:
        """
        Convert a segmentation array into a SimpleITK Image.
        """
        return legacy_build_nifty_image(segmentation)

    def preprocess(self, sequence: np.ndarray, **kwargs) -> np.ndarray:
        """
        MRI-specific preprocessing. Currently returns the sequence as-is,
        or could integrate legacy fit_brain_boundaries if needed here.
        """
        # MRI doesn't currently apply mandatory speckle reduction etc at this general layer in AUDIT
        # If needed, it can be passed through here.
        return sequence

    def run_comparison_segmentation_viewer(
        self, path_seg: str, path_pred: str, case: str, labels: Optional[Dict] = None
    ) -> bool:
        """
        Runs ITK-SNAP to compare segmentations for MRI.
        """
        return legacy_itk_snap(path_seg, path_pred, case, labels)

    def get_default_sequences(self) -> List[str]:
        """
        Returns default MRI sequences.
        """
        return ["_t1", "_t1ce", "_t2", "_flair"]

    def get_default_format(self) -> str:
        return ".nii.gz"
