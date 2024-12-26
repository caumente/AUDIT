from collections import Counter

import numpy as np
from loguru import logger
from scipy.spatial.distance import euclidean

from src.utils.commons.strings import add_prefix_dict


class TumorFeatures:
    """
    A class to compute tumor features from given medical segmentation.

    Attributes:
    ----------
    segmentation : np.ndarray
        A numpy array representing the segmentation of the medical image.
    spacing : tuple, optional
        A tuple representing the voxel spacing of the image.
    mapping_names : dict, optional
        A dictionary to map segmentation values to names.

    Methods:
    -------
    count_tumor_pixels():
        Counts the number of pixels for each unique value in the segmentation.

    calculate_lesion_size():
        Calculates the lesion size in the segmentation.

    calculate_tumor_center_mass(label=None):
        Calculates the center of mass for the tumor in the image.

    get_tumor_slices():
        Gets the slices that contain tumor regions in axial, coronal, and sagittal planes.
    """

    def __init__(self, segmentation, spacing=(1, 1, 1), mapping_names=None, planes=None):
        """
        Constructs all the necessary attributes for the TumorAnalysis object.

        Parameters:
        ----------
        segmentation : np.ndarray
            A numpy array representing the segmentation of the medical image.
        image : np.ndarray, optional
            A numpy array representing the medical image.
        spacing : tuple, optional
            A tuple representing the voxel spacing of the image (default is (1, 1, 1)).
        mapping_names : dict, optional
            A dictionary to map segmentation values to names.
        """
        self.center_mass_dict = None
        self.lesion_size = None
        self.tumor_location = None
        self.number_pixels = None
        self.tumor_slices = None
        self.position_tumor_slices = None
        self.segmentation = segmentation
        self.spacing = np.array(spacing)
        self.mapping_names = mapping_names
        self.planes = planes if planes is not None else ["axial", "coronal", "sagittal"]
        self.tumor_centre_mass_per_label = {}

    def count_tumor_pixels(self):
        """
        Counts the number of pixels for each unique value in the segmentation.

        Returns:
        -------
        dict
            A dictionary with the counts of each unique value in the segmentation.
        """
        if self.segmentation is None:
            if self.mapping_names:
                return {k.lower(): np.nan for k in self.mapping_names.values()}
            else:
                return {}

        unique, counts = np.unique(self.segmentation, return_counts=True)
        pixels_dict = dict(zip(unique, counts))

        if self.mapping_names:
            pixels_dict = {str(self.mapping_names.get(k, k)).lower(): v for k, v in pixels_dict.items()}

        return pixels_dict

    def calculate_lesion_size(self):
        """
        Calculates the lesion size in the segmentation.

        Returns:
        -------
        dict
            A dictionary containing the lesion size.
        """
        if self.segmentation is None:
            return {"lesion_size": np.nan}

        lesion_size = (self.segmentation > 0).sum() * np.prod(self.spacing)
        return {"lesion_size": lesion_size}

    def get_tumor_center_mass(self, label=None):
        """
        Calculates the center of mass for the tumor in the image.

        Parameters:
        ----------
        label : int, optional
            The label value of the tumor (default is None).

        Returns:
        -------
        np.ndarray
            The center of mass coordinates adjusted by the voxel spacing.
        """
        if self.segmentation is None:
            logger.warning("Segmentation is required to calculate the tumor center of mass. Assigning (nan, nan, nan)")
            return np.array([np.nan] * 3)

        if label is not None and not np.any(self.segmentation == label):
            logger.warning(f"Label {label} not found in segmentation.")
            return np.array([np.nan] * len(self.segmentation.shape))

        coordinates = np.argwhere(self.segmentation == label) if label != 0 else np.argwhere(self.segmentation != 0)
        if coordinates.size == 0:
            logger.warning("No tumor coordinates found. Assigning (nan, nan, nan)")
            return np.array([np.nan] * len(self.segmentation.shape))

        center_of_mass_mean = np.mean(coordinates, axis=0)
        return center_of_mass_mean * self.spacing

    def get_tumor_slices(self):
        if self.segmentation is None:
            return np.nan, np.nan, np.nan

        axial_dim, coronal_dim, sagittal_dim = self.segmentation.shape
        axial_tumor_slices, coronal_tumor_slices, sagittal_tumor_slices = [], [], []

        # axial plane
        for n, s in enumerate(range(axial_dim)):
            slc = self.segmentation[s, :, :]
            if Counter(slc.flatten()).get(0) != (coronal_dim * sagittal_dim):
                axial_tumor_slices.append(n)

        # coronal plane
        for n, s in enumerate(range(coronal_dim)):
            slc = self.segmentation[:, s, :]
            if Counter(slc.flatten()).get(0) != (axial_dim * sagittal_dim):
                coronal_tumor_slices.append(n)

        # sagittal plane
        for n, s in enumerate(range(sagittal_dim)):
            slc = self.segmentation[:, :, s]
            if Counter(slc.flatten()).get(0) != (axial_dim * coronal_dim):
                sagittal_tumor_slices.append(n)

        return axial_tumor_slices, coronal_tumor_slices, sagittal_tumor_slices

    def calculate_tumor_slices(self):
        if self.segmentation is None:
            return {f"{k}_tumor_slice": np.nan for k, v in dict(zip(self.planes, self.get_tumor_slices())).items()}

        return {f"{k}_tumor_slice": len(v) for k, v in dict(zip(self.planes, self.get_tumor_slices())).items()}

    def calculate_position_tumor_slices(self):
        position_tumor_slices = {}
        if self.segmentation is None:
            position_tumor_slices.update({f"lower_{k}_tumor_slice": np.nan for k, v in
                                          dict(zip(self.planes, self.get_tumor_slices())).items()})
            position_tumor_slices.update({f"upper_{k}_tumor_slice": np.nan for k, v in
                                          dict(zip(self.planes, self.get_tumor_slices())).items()})
        else:
            position_tumor_slices.update({f"lower_{k}_tumor_slice": np.min(v) for k, v in
                                          dict(zip(self.planes, self.get_tumor_slices())).items()})
            position_tumor_slices.update({f"upper_{k}_tumor_slice": np.max(v) for k, v in
                                          dict(zip(self.planes, self.get_tumor_slices())).items()})

        return position_tumor_slices

    def calculate_tumor_pixel(self):
        if self.segmentation is None:
            return {f"lesion_size_{k.lower()}": np.nan for k in self.mapping_names.values()}

        number_pixels = self.count_tumor_pixels()
        number_pixels.pop("bkg", None)
        number_pixels = {key: int(value * self.spacing.prod()) for key, value in number_pixels.items()}
        self.number_pixels = add_prefix_dict(number_pixels, prefix="lesion_size_")

        return self.number_pixels

    def calculate_tumor_distance(self, brain_centre_mass):
        tumor_location = {}

        if np.isnan(list(brain_centre_mass)).any()or not bool(brain_centre_mass):
            logger.warning("Tumor location calculation failed. Assigning (nan, nan, nan)")
            return {f"{k}_tumor_location": np.nan for k in self.tumor_centre_mass_per_label}

        for k, v in self.tumor_centre_mass_per_label.items():
            if not np.isnan(v).any():
                tumor_location[f"{k}_tumor_location"] = euclidean(list(brain_centre_mass), v)
            else:
                tumor_location[f"{k}_tumor_location"] = np.nan
        return tumor_location

    def calculate_tumor_center_mass(self):
        for idx, name in self.mapping_names.items():
            if name == "BKG":
                name = "WHOLE"
            self.tumor_centre_mass_per_label[name.lower()] = self.get_tumor_center_mass(label=idx)

        # Flatten the dictionary to get the center of mass in each plane
        center_mass_dict = {
            f"{plane}_{label}_center_mass": coord
            for label, coords in self.tumor_centre_mass_per_label.items()
            for plane, coord in zip(["axial", "coronal", "sagittal"], coords)
        }

        return center_mass_dict

    def extract_features(self, brain_centre_mass) -> dict:
        """
        Extracts all tumor-related features.

        Returns:
        -------
        dict
            A dictionary containing all tumor features.
        """

        # calculate the center of mass of the whole tumor and each label
        self.center_mass_dict = self.calculate_tumor_center_mass()

        # calculate tumor location for each label
        self.tumor_location = self.calculate_tumor_distance(brain_centre_mass)

        # calculate the number of tumor slices
        self.tumor_slices = self.calculate_tumor_slices()

        # calculate the minimum and maximum tumor slice per plane
        self.position_tumor_slices = self.calculate_position_tumor_slices()

        # calculate number of tumor pixels
        self.number_pixels = self.calculate_tumor_pixel()

        # calculate lesion size
        self.lesion_size = self.calculate_lesion_size()

        # Combine all features into a single dictionary
        return {
            **self.center_mass_dict,
            **self.tumor_location,
            **self.number_pixels,
            **self.lesion_size,
            **self.tumor_slices,
            **self.position_tumor_slices
        }
