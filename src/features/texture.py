import numpy as np
from skimage.feature import graycomatrix
from skimage.feature import graycoprops

from src.utils.sequences.sequences import fit_brain_boundaries


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
        if self.remove_empty_planes:
            sequence = fit_brain_boundaries(self.sequence)

        # Normalize the image to values between 0 and 255
        image_array = (255 * (sequence - np.min(sequence)) / (np.max(sequence) - np.min(sequence))).astype(np.uint8)

        # Define distances and angles for GLCM calculation
        distances = [1]
        angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]

        # Initialize a list to store the texture values for each plane
        texture_values = []

        # Iterate over each 2D plane in the Z dimension
        for z in range(image_array.shape[0]):
            plane = image_array[z, :, :]

            # Compute GLCM for the current plane
            glcm = graycomatrix(plane, distances=distances, angles=angles, levels=256, symmetric=True, normed=True)

            # Compute the texture feature using skimage.feature.graycoprops
            feature_value = graycoprops(glcm, prop=texture).mean()

            # Store the texture value of the current plane
            texture_values.append(feature_value)

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
            textures = ['contrast', 'dissimilarity', 'homogeneity', 'ASM', 'energy', 'correlation']

        features = {}
        for texture in textures:
            texture_values = self.compute_texture_values(texture=texture)

            # Create a dictionary to store texture features
            features.update({f"mean_{texture}": np.mean(texture_values)})
            features.update({f"std_{texture}": np.std(texture_values)})

        return features
