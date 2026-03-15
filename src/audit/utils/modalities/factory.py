from .base import ModalityBase
from .mri import MRIModality
from .us import USModality


def get_modality(modality_name: str) -> ModalityBase:
    """
    Factory function to get the appropriate Modality implementation.
    """
    modality_name = modality_name.upper()
    if modality_name == "MRI":
        return MRIModality()
    elif modality_name == "US":
        return USModality()
    else:
        raise ValueError(f"Unsupported modality: {modality_name}. Supported: 'MRI', 'US'.")
