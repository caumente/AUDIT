from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np


class ModalityBase(ABC):
    """
    Abstract base class for imaging modalities (e.g., MRI, US).
    This class defines the interface for modality-specific operations.
    """

    @abstractmethod
    def load_sequence(self, path: str, as_array: bool = False) -> Optional[Union[object, np.ndarray]]:
        """
        Loads a single image/sequence from disk.
        """
        pass

    @abstractmethod
    def read_sequences_dict(
        self, root_dir: str, subject_id: str, sequences: Optional[List[str]] = None
    ) -> Dict[str, Optional[np.ndarray]]:
        """
        Reads all relevant sequences for a subject and returns them as a dictionary.
        """
        pass

    @abstractmethod
    def get_spacing(self, img: Optional[object]) -> np.ndarray:
        """
        Retrieves the voxel/pixel spacing of the image.
        """
        pass

    @abstractmethod
    def build_image(self, segmentation: Union[np.ndarray, list]) -> object:
        """
        Converts a segmentation array into the modality's specific image format (e.g., SimpleITK Image).
        """
        pass

    @abstractmethod
    def preprocess(self, sequence: np.ndarray, **kwargs) -> np.ndarray:
        """
        Applies modality-specific preprocessing (e.g., filtering, normalization).
        """
        pass

    @abstractmethod
    def run_comparison_segmentation_viewer(
        self, path_seg: str, path_pred: str, case: str, labels: Optional[Dict] = None
    ) -> bool:
        """
        Runs an external viewer (like ITK-SNAP) to compare ground truth and predicted segmentations.
        """
        pass

    @abstractmethod
    def get_default_sequences(self) -> List[str]:
        """
        Returns the default list of sequences expected by this modality.
        """
        pass
