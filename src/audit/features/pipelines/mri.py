from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd

from audit.features.extractors.spatial import SpatialFeatures
from audit.features.extractors.statistical import StatisticalFeatures
from audit.features.extractors.texture import TextureFeatures
from audit.features.extractors.tumor import TumorFeatures
from audit.features.pipelines.base import FeaturePipelineBase


class MRIPipeline(FeaturePipelineBase):
    """
    Feature extraction pipeline tailored for 3D MRI.
    Extracts Spatial, Tumor, Statistical, and Texture features.
    """

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
        spatial_features, tumor_features, stats_features, texture_feats = {}, {}, {}, {}

        # 1. Statistical features
        if "statistical" in self.features_to_extract:
            stats_features = {
                key: StatisticalFeatures(seq[seq > 0]).extract_features()
                for key, seq in sequences.items()
                if seq is not None
            }

        # 2. Texture features
        if "texture" in self.features_to_extract:
            texture_feats = {
                key: TextureFeatures(seq, remove_empty_planes=True).extract_features()
                for key, seq in sequences.items()
                if seq is not None
            }

        # 3. Spatial features
        if "spatial" in self.features_to_extract:
            # For MRI, seq_reference determines the sequence for spatial features
            safe_reference_key = (
                seq_reference.replace("_", "") if seq_reference else (list(sequences.keys())[0] if sequences else None)
            )
            sf = SpatialFeatures(sequence=sequences.get(safe_reference_key), spacing=sequences_spacing)
            spatial_features = sf.extract_features()

        # 4. Tumor features
        if "tumor" in self.features_to_extract:
            mapping_names = dict(zip(numeric_label, label_names)) if numeric_label and label_names else {}
            tf = TumorFeatures(segmentation=segmentation, spacing=seg_spacing, mapping_names=mapping_names)
            center_mass_fallback = sf.center_mass.values() if "spatial" in self.features_to_extract else {}
            tumor_features = tf.extract_features(center_mass_fallback)

        return self._compile_subject_info(subject_id, spatial_features, tumor_features, stats_features, texture_feats)
