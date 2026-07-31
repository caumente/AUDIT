from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd


class FeaturePipelineBase(ABC):
    """
    Abstract base class for modality-specific feature extraction pipelines.
    """

    def __init__(self, features_to_extract: List[str], modality_name: str, cpu_cores: int = 1):
        self.features_to_extract = features_to_extract
        self.modality_name = modality_name
        self.cpu_cores = cpu_cores

    @abstractmethod
    def extract(
        self,
        subject_id: str,
        sequences: Dict[str, Optional[np.ndarray]],
        segmentation: Optional[np.ndarray] = None,
        sequences_spacing: Optional[np.ndarray] = None,
        seg_spacing: Optional[np.ndarray] = None,
        seq_reference: Optional[str] = None,
        numeric_label: Optional[List[int]] = None,
        label_names: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Executes the modality-specific feature extraction logic.

        Args:
            subject_id: ID of the subject.
            sequences: Dictionary mapping sequence names to image arrays.
            segmentation: Numpy array of the segmentation mask.
            sequences_spacing: Spacing of the base sequences.
            seg_spacing: Spacing of the segmentation mask.
            seq_reference: Name of the reference sequence (e.g. '_t1').
            numeric_label: List of numeric labels mapped to tumor regions.
            label_names: List of string names mapped to tumor regions.

        Returns:
            A pandas DataFrame containing a single row with all extracted features.
        """
        pass

    def _compile_subject_info(
        self, subject_id: str, spatial_features: dict, tumor_features: dict, stats_features: dict, texture_feats: dict
    ) -> pd.DataFrame:
        """
        Helper method to compile feature dictionaries into a single flat DataFrame.
        """
        subject_info = {"ID": subject_id}

        # Add spatial/tumor information directly
        subject_info.update(spatial_features)
        subject_info.update(tumor_features)

        # Prepend sequence name to stats information
        for seq, dict_stats in stats_features.items():
            prefixed_stats = {f"{seq}_{k}" if seq != "default" else k: v for k, v in dict_stats.items()}
            subject_info.update(prefixed_stats)

        # Prepend sequence name to texture information
        for seq, dict_stats in texture_feats.items():
            prefixed_textures = {f"{seq}_{k}" if seq != "default" else k: v for k, v in dict_stats.items()}
            subject_info.update(prefixed_textures)

        return pd.DataFrame(subject_info, index=[0])
