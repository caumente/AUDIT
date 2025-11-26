The `TextureFeatures` class provides an efficient mechanism for calculating second-order texture features from a given
3D magnetic resonance image (MRI).

---

## __Overview__

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

---

## __Methods__

### `__init__`

Constructs all the necessary attributes for the TextureFeatures object.

**Parameters**  

- **sequence** (`np.ndarray`): A 3D NumPy array representing the MRI image.  
- **remove_empty_planes** (`bool`, default: `False`): Whether to remove empty (non-brain) planes before processing.

---

### `compute_texture_values`

Computes texture values for each 2D plane in the 3D image array.

**Parameters**  

- **texture** (`str`): The texture feature to compute (default is `"contrast"`).

**Returns**  

- `np.ndarray`: An array of texture values for each 2D plane in the image.

---

### `extract_features`

Extracts texture features from the MRI image by calculating statistical summaries for multiple texture metrics.

**Parameters**  

- **textures** (`list[str]`, optional): A list of texture features to compute (e.g., `'contrast'`, `'energy'`).  
  Defaults to `['contrast', 'dissimilarity', 'homogeneity', 'ASM', 'energy', 'correlation']`.

**Returns**  

A dictionary where keys represent texture feature names, and values represent the mean and standard deviation for each feature.

---