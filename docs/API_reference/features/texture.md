[//]: # (::: src.features.texture.TextureFeatures)


The `TextureFeatures` class provides an efficient mechanism for calculating second-order texture features from a given
3D magnetic resonance image (MRI).

### Overview

This class utilizes **skimage** for calculating the gray level co-occurrence matrix (GLCM) and its corresponding texture 
features such as contrast, homogeneity, and energy. The texture features extracted from each 2D plane of a 3D MRI 
sequence give insights into the structural patterns within the image.

By encapsulating these operations in a class, the user can easily compute several texture features with minimal effort.
It also supports an option to remove empty planes, improving accuracy when working with brain MRI scans.

The following texture features are available:

- **Contrast**: A measure of the intensity contrast between a pixel and its neighbor over the whole image.
- **Dissimilarity**: Measures the local intensity variations.
- **Homogeneity**: Measures the closeness of the distribution of elements in the GLCM to the GLCM diagonal.
- **ASM (Angular Second Moment)**: A measure of the texture uniformity.
- **Energy**: The square root of ASM, indicating the texture’s level of orderliness.
- **Correlation**: A measure of how correlated a pixel is to its neighbor across the whole image.

### Methods

#### `__init__()`

**Description**:

The constructor initializes a `TextureFeatures` object by accepting a 3D MRI sequence and an optional parameter to 
remove empty planes. The class will compute texture features across 2D planes, making use of GLCM-based calculations.

**Parameters**:

- sequence (np.ndarray): A 3D MRI image in the form of a NumPy array from which texture features will be calculated.
- remove_empty_planes (bool): A flag to indicate whether empty planes (e.g., non-brain areas) should be removed from the MRI sequence. Defaults to False. 

----------------------------  

#### `compute_texture_values()`

**Description**:
Computes the specified texture feature for each 2D plane in the 3D image. The GLCM is calculated for each 2D slice, and the texture feature is extracted using graycoprops from the skimage.feature module.

**Parameters**:

- `texture` (`str`): The texture feature to compute (e.g., "contrast", "homogeneity"). Defaults to "contrast".

Returns (`np.ndarray`): An array of texture values for each 2D plane in the 3D MRI sequence.

----------------------------  

#### `extract_features()`
Description:

Extracts all specified texture features from the MRI image. This method iterates through the given list of texture features, computing the mean and standard deviation for each one across all 2D planes in the MRI sequence.

**Parameters**:

- `textures` (`list[str]): A list of texture features to compute (e.g., 'contrast', 'energy'). If not provided, the 
    default set includes: 'contrast', 'dissimilarity', 'homogeneity', 'ASM', 'energy', 'correlation'

Returns (`dict`): A dictionary where the keys represent the texture feature names, and the values represent the mean 
and standard deviation for each feature.

