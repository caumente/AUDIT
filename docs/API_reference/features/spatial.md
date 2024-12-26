[//]: # (::: src.features.spatial.SpatialFeatures)


The `SpatialFeatures` class is designed to compute spatial properties related to 3D medical imaging sequences, such as 
brain MRI scans. This class focuses on calculating basic spatial features like the brain's center of mass and the 
dimensionality of the scan in various planes.

### Overview

This class is intended to provide spatial insights from a 3D sequence of medical images. It helps to extract two key 
metrics: The center of mass for the brain, which is calculated based on the sequence. The dimensions of the sequence in
the axial, coronal, and sagittal planes. These spatial features are essential in understanding the brain's structure 
and alignment in a 3D scan, aiding in medical analysis and further processing of brain images.

The following spatial features are available:

- **Brain Center of Mass**: The 3D coordinates of the brain's center, adjusted by voxel spacing.
- **Sequence Dimensions**: The dimensions of the sequence in the axial, coronal, and sagittal planes.


### Methods

#### `__init__()`

**Description**:  
The constructor method initializes a `SpatialFeatures` object with a given 3D image sequence and voxel spacing. The 
voxel spacing is used for any adjustments to the spatial features (e.g., center of mass). If no spacing is provided, 
it defaults to (1, 1, 1).

**Parameters**:

- `sequence` (`np.ndarray`): A 3D MRI in form of NumPy array from which spatial features will be calculated.
- `spacing` (`np.ndarray, optional`): A tuple representing the voxel spacing of the medical image. Defaults to 
(1, 1, 1) if not provided.

----------------------------  

#### `calculate_brain_center_mass()`

Returns (`dict`): A dictionary containing the 3D coordinates of the brain's center of mass for each plane (axial, 
coronal, sagittal), adjusted by the voxel spacing. If the sequence is not found, it returns NaN for each plane.

----------------------------  

#### `get_dimensions()`

Returns (`dict`): A dictionary containing the dimensions of the sequence for each plane (axial_dim, coronal_dim, and 
sagittal_dim). If the sequence is not found, the dimensions are returned as NaN.

----------------------------  

#### `extract_features()`

Returns (`dict`): All spatial features. 

- `axial_dim`: Number of slices in the axial plane.
- `coronal_dim`: Number of slices in the coronal plane.
- `sagittal_dim`: Number of slices in the sagittal plane.
- `axial_brain_centre_mass`: The center of mass in the axial plane.
- `coronal_brain_centre_mass`: The center of mass in the coronal plane.
- `sagittal_brain_centre_mass`: The center of mass in the sagittal plane.

