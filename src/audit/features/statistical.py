import numpy as np
from scipy.stats import kurtosis
from scipy.stats import skew


class StatisticalFeatures:
    """
    A class to compute statistical features from a given sequence.

    Attributes:
    ----------
    sequence : np.ndarray
        A numpy array representing the sequence from which statistical features are to be computed.

    Methods:
    -------
    get_max_intensity():
        Computes the maximum intensity value in the sequence.

    get_min_intensity():
        Computes the minimum intensity value in the sequence.

    get_mean_intensity():
        Computes the mean intensity value in the sequence.

    get_median_intensity():
        Computes the median intensity value in the sequence.

    get_std_intensity():
        Computes the standard deviation of intensity values in the sequence.

    get_range_intensity():
        Computes the range of intensity values in the sequence (max - min).

    get_skewness():
        Computes the skewness of the intensity values in the sequence.

    get_kurtosis():
        Computes the kurtosis of the intensity values in the sequence.

    get_stats_from_sequence():
        Computes and returns all statistical metrics as a dictionary.
    """

    def __init__(self, sequence):
        """
        Constructs all the necessary attributes for the StatisticalFeatures object.

        Parameters:
        ----------
        sequence : np.ndarray
            A numpy array representing the sequence from which statistical features are to be computed.
        """
        self.sequence = sequence

    def get_max_intensity(self):
        """Computes the maximum intensity value in the sequence."""
        return self.sequence.max()

    def get_min_intensity(self):
        """Computes the minimum intensity value in the sequence."""
        return self.sequence.min()

    def get_mean_intensity(self):
        """Computes the mean intensity value in the sequence."""
        return self.sequence.mean()

    def get_median_intensity(self):
        """Computes the median intensity value in the sequence."""
        return np.median(self.sequence)

    def get_percentile_n(self, n):
        """Computes the n-th percentile of the intensity values in the sequence."""
        return np.percentile(self.sequence, n)

    def get_std_intensity(self):
        """Computes the standard deviation of intensity values in the sequence."""
        return self.sequence.std()

    def get_range_intensity(self):
        """Computes the range of intensity values in the sequence (max - min)."""
        return self.sequence.max() - self.sequence.min()

    def get_skewness(self):
        """Computes the skewness of the intensity values in the sequence."""
        return skew(self.sequence.flatten())

    def get_kurtosis(self):
        """Computes the kurtosis of the intensity values in the sequence."""
        return kurtosis(self.sequence.flatten())

    def extract_features(self):
        """
        Computes and returns all statistical metrics as a dictionary.

        Returns:
        -------
        dict
            A dictionary containing the following statistical metrics:
            - max_intensity
            - min_intensity
            - mean_intensity
            - median_intensity
            - 10_percentile_intensity
            - 90_percentile_intensity
            - std_intensity
            - range_intensity
            - skewness
            - kurtosis
        """
        return {
            "max_intensity": self.get_max_intensity(),
            "min_intensity": self.get_min_intensity(),
            "mean_intensity": self.get_mean_intensity(),
            "median_intensity": self.get_median_intensity(),
            "10_perc_intensity": self.get_percentile_n(10),
            "90_perc_intensity": self.get_percentile_n(90),
            "std_intensity": self.get_std_intensity(),
            "range_intensity": self.get_range_intensity(),
            "skewness": self.get_skewness(),
            "kurtosis": self.get_kurtosis(),
        }
