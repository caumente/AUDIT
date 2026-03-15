from typing import Type

from loguru import logger

from audit.features.pipelines.base import FeaturePipelineBase


def get_feature_pipeline(modality_name: str) -> Type[FeaturePipelineBase]:
    """
    Returns the appropriate pipeline class for the specified modality.
    """
    modality_name = modality_name.upper()
    if modality_name == "MRI":
        from audit.features.pipelines.mri import MRIPipeline

        return MRIPipeline
    elif modality_name == "US":
        from audit.features.pipelines.us import USPipeline

        return USPipeline
    else:
        logger.warning(f"Modality '{modality_name}' not natively mapped. Defaulting to MRIPipeline as fallback.")
        from audit.features.pipelines.mri import MRIPipeline

        return MRIPipeline
