import numpy as np
from loguru import logger


class SpatialFeatures:
    """
    A class to compute spatial features from sequences given magnetic resonance images.

    Attributes:
    ----------
    sequence : np.ndarray
        A numpy array representing the sequence associated with the medical image.
    spacing : np.ndarray
        A numpy array representing the spacing of the medical image voxels.

    Methods:
    -------
    calculate_anatomical_center_mass():
        Calculates the center of mass for the anatomical image.
    get_dimensions():
        Gets the dimensions of the sequence in axial, coronal, and sagittal planes.
    """

    def __init__(self, sequence, spacing=None):
        """
        Constructs all the necessary attributes for the SpatialFeatures object.

        Parameters:
        ----------
        sequence : np.ndarray
            A numpy array representing the sequence associated with the medical image.
        segmentation : np.ndarray
            A numpy array representing the segmentation of the medical image.
        spacing : np.ndarray
            A numpy array representing the spacing of the medical image voxels.
        """
        self.center_mass = None
        self.dimensions = None
        self.sequence = sequence
        self.spacing = spacing if spacing is not None else (1, 1, 1)

    def calculate_anatomical_center_mass(self):
        """
        Calculates the center of mass for the anatomical image.

        Returns:
        -------
        np.ndarray
            The center of mass coordinates adjusted by the voxel spacing.
        """
        if self.sequence is None:
            logger.warning("Sequence not found. Assigning center of mass (nan, nan, nan)")
            return {
                "axial_plane_center_of_mass": np.nan,
                "coronal_plane_center_of_mass": np.nan,
                "sagittal_plane_center_of_mass": np.nan,
            }

        # Get the indices of the non-zero voxels
        coordinates = np.argwhere(self.sequence != 0)

        # Calculate the center of mass
        center_of_mass_mean = np.mean(coordinates, axis=0)

        if len(center_of_mass_mean) == 3:
            keys = ["axial_plane_center_of_mass", "coronal_plane_center_of_mass", "sagittal_plane_center_of_mass"]
        elif len(center_of_mass_mean) == 2:
            keys = ["height_center_of_mass", "width_center_of_mass"]
        else:
            keys = [f"dim_{i}_center_of_mass" for i in range(len(center_of_mass_mean))]

        return dict(zip(keys, center_of_mass_mean * self.spacing[: len(keys)]))

    def get_shape(self):
        """
        Gets the dimensions of the sequence in axial, coronal, and sagittal planes (if 3D).
        For 2D images, dimensions map strictly to height and width.

        Returns:
        -------
        dict
            A dictionary containing the dimensions of the sequence.
        """
        if self.sequence is None:
            logger.warning("Sequence not found. Assigning dimensions (nan, nan, nan)")
            return {
                "axial_plane_resolution": np.nan,
                "coronal_plane_resolution": np.nan,
                "sagittal_plane_resolution": np.nan,
            }

        shape = self.sequence.shape
        if len(shape) == 3:
            axial, coronal, sagittal = shape
            dimensions = {
                "axial_plane_resolution": int(axial),
                "coronal_plane_resolution": int(coronal),
                "sagittal_plane_resolution": int(sagittal),
            }
        elif len(shape) == 2:
            height, width = shape
            dimensions = {
                "height_resolution": int(height),
                "width_resolution": int(width),
                "depth_resolution": 1,
            }
        else:
            dimensions = {f"dim_{i}_resolution": int(s) for i, s in enumerate(shape)}

        return dimensions

    def extract_features(self) -> dict:
        """
        Extracts all tumor-related features.

        Returns:
        -------
        dict
            A dictionary containing all tumor features.
        """

        # Calculate the center of mass of the whole tumor and each label
        self.dimensions = self.get_shape()

        self.center_mass = self.calculate_anatomical_center_mass()

        # Combine all features into a single dictionary
        return {**self.dimensions, **self.center_mass}
