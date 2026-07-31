import numpy as np
from skimage.feature import graycomatrix
from skimage.feature import graycoprops

from audit.utils.sequences.sequences import crop_nonzero_region
from audit.utils.sequences.sequences import fit_brain_boundaries


class TextureFeatures:
    """
    A class to compute second order texture features from a given MRI image.

    Attributes:
    ----------
    image_array : np.ndarray
        A 3D numpy array representing the MRI image.

    Methods:
    -------
    compute_texture_values(texture="contrast"):
        Computes texture values for each 2D plane in the 3D image array.
    extract_features(texture="contrast") -> dict:
        Extracts texture features from the MRI image.
    """

    def __init__(self, sequence: np.array, remove_empty_planes: bool = False):
        """
        Constructs all the necessary attributes for the TextureFeatures object.

        Parameters:
        ----------
        sequence : np.ndarray
            A 3D numpy array representing the MRI image.
        """
        self.sequence = sequence
        self.remove_empty_planes = remove_empty_planes

    def compute_texture_values(self, texture: str = None):
        """
        Computes texture values for each 2D plane in the 3D image array.

        Parameters:
        ----------
        texture : str
            The texture feature to compute (default is "contrast").

        Returns:
        -------
        np.ndarray
            An array of texture values for each 2D plane in the image.
        """
        if texture is None:
            texture = []

        if np.all(self.sequence == 0):
            return np.nan

        sequence = self.sequence.copy()
        # TODO: each modality and organ might have their own particularities. Excluding empty/constant planes
        if self.remove_empty_planes:
            sequence = crop_nonzero_region(self.sequence)
            # sequence = fit_brain_boundaries(self.sequence)

        # Normalize the image to values between 0 and 255. A non-zero
        # constant image has a valid (uniform) GLCM and must not divide by 0.
        sequence_min = np.min(sequence)
        sequence_range = np.max(sequence) - sequence_min
        if sequence_range == 0:
            image_array = np.zeros_like(sequence, dtype=np.uint8)
        else:
            image_array = (255 * (sequence - sequence_min) / sequence_range).astype(np.uint8)

        # Define distances and angles for GLCM calculation
        distances = [1]
        angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]

        # Initialize a list to store the texture values for each plane
        texture_values = []

        dims = len(image_array.shape)

        # Iterate over each 2D plane in the Z dimension if 3D, otherwise just process the single plane
        if dims >= 3:
            for z in range(image_array.shape[0]):
                plane = image_array[z, :, :]

                # TODO: each modality and organ might have their own particularities. Excluding empty/constant planes
                # if np.all(plane == 0):
                #     continue
                # if np.all(plane == plane.flat[0]): possible solution when values are the same in a slice but not zero (CT)
                #     continue

                # Compute GLCM for the current plane
                glcm = graycomatrix(plane, distances=distances, angles=angles, levels=256, symmetric=True, normed=True)

                # Compute the texture feature using skimage.feature.graycoprops
                feature_value = graycoprops(glcm, prop=texture).mean()

                # Store the texture value
                texture_values.append(feature_value)
        elif dims == 2:
            plane = image_array

            # Compute GLCM for the single 2D plane. An all-zero normalized
            # plane can represent a non-zero constant source image.
            glcm = graycomatrix(plane, distances=distances, angles=angles, levels=256, symmetric=True, normed=True)
            feature_value = graycoprops(glcm, prop=texture).mean()
            texture_values.append(feature_value)

        if not texture_values:
            return np.array([np.nan])

        return np.array(texture_values)

    def extract_features(self, textures: list = None) -> dict:
        """
        Extracts texture features from the MRI image.

        Parameters:
        ----------
        texture : str
            The texture feature to compute (default is "contrast").

        Returns:
        -------
        dict
            A dictionary containing texture features for each plane.
        """
        if not textures:
            textures = ["contrast", "dissimilarity", "homogeneity", "ASM", "energy", "correlation"]

        features = {}
        for texture in textures:
            texture_values = self.compute_texture_values(texture=texture)

            # Create a dictionary to store texture features
            features.update({f"mean_{texture.lower()}": np.mean(texture_values)})
            features.update({f"std_{texture.lower()}": np.std(texture_values)})

        return features
