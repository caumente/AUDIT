import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import SimpleITK
from loguru import logger

from audit.utils.external_tools.itk_snap import run_comparison_segmentation_itk_snap as legacy_itk_snap
from audit.utils.modalities.base import ModalityBase
from audit.utils.sequences.sequences import build_nifty_image as legacy_build_nifty_image
from audit.utils.sequences.sequences import get_spacing as legacy_get_spacing
from audit.utils.sequences.sequences import load_nii
from audit.utils.sequences.sequences import read_sequences_dict as legacy_read_sequences_dict


class MRIModality(ModalityBase):
    """
    MRI Modality implementation.
    Wraps existing MRI logic from sequences.py and itk_snap.py.
    """

    def load_sequence(self, path: str, as_array: bool = False) -> Optional[Union[SimpleITK.Image, np.ndarray]]:
        """
        Load a NIfTI image from disk for MRI.
        """
        return load_nii(path, as_array)

    def read_sequences_dict(
        self, root_dir: str, subject_id: str, sequences: Optional[List[str]] = None
    ) -> Dict[str, Optional[np.ndarray]]:
        """
        Read multiple NIfTI sequences for an MRI subject.
        """
        return legacy_read_sequences_dict(root_dir, subject_id, sequences)

    def get_spacing(self, img: Optional[SimpleITK.Image]) -> np.ndarray:
        """
        Get voxel spacing of a SimpleITK image.
        """
        return legacy_get_spacing(img)

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
