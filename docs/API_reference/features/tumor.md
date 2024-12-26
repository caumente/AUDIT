[//]: # (::: src.features.tumor.TumorFeatures)


The `TumorFeatures` class computes various tumor-related metrics based on a segmented 3D medical image, such as lesion 
size, tumor center of mass, and tumor location relative to the brain's center of mass.

### Overview

This class provides methods to compute first-order tumor features, focusing on spatial and volumetric characteristics 
derived from medical image segmentation. It is designed to handle common use cases in medical imaging, such as 
identifying tumor regions, calculating the tumor's size, and determining its relative position.

The class allows customization through optional parameters such as voxel spacing and segmentation label mappings. This 
makes it highly adaptable to different medical imaging contexts, including various scan types and segmentation 
algorithms.


The following tumor features are available:

- **Tumor Pixel Count**: The number of pixels associated with each tumor label in the segmentation.
- **Lesion Size**: The volume of the lesion(s) computed based on pixel count and voxel spacing.
- **Tumor Center of Mass**: The geometric center of a tumor or lesion in 3D space.
- **Tumor Slices**: The image slices in the axial, coronal, and sagittal planes that contain tumor regions.
- **Tumor Position**: The location of tumor slices in each plane (e.g., lower and upper bounds).


### Methods

#### `__init__()`

**Description**:  
The constructor initializes a `TumorFeatures` object using a 3D segmented MRI and various optional parameters such as 
voxel spacing and label mappings. These attributes are used to calculate tumor features like lesion size and tumor 
location across different planes.

**Parameters**:

- `segmentation` (`np.ndarray`): A 3D NumPy array representing the segmentation of the medical image.
- `spacing` (`tuple, optional`): The voxel spacing of the medical image (default is (1, 1, 1)).
- `mapping_names` (`dict, optional`): A dictionary mapping segmentation values (labels) to human-readable names.
- `planes` (`list[str]`, optional`): The planes (axial, coronal, sagittal) for tumor slice analysis. Defaults to 
["axial", "coronal", "sagittal"].

----------------------------  

#### `count_tumor_pixels()`

Returns (`dict`):  A dictionary where keys represent segmentation labels (or names) and values represent the pixel 
count for each label.

----------------------------  

#### `count_tumor_pixels()`

Returns (`dict`): A dictionary containing the total lesion size, keyed by "lesion_size".

----------------------------  

#### `get_tumor_center_mass(label=None)`

**Parameters**:

- `label` (`int, optional`): Specifies the label of the tumor for which the center of mass should be calculated. If not 
provided, the calculation is done for all tumor regions.

Return (`np.ndarray`): The 3D coordinates of the tumor’s center of mass.

----------------------------  

#### `get_tumor_slices()`

Return (`tuple`): A tuple containing three lists, each representing the indices of slices with tumors in the axial, 
coronal, and sagittal planes.

----------------------------  

#### `calculate_tumor_slices()`

Return (`dict`): A dictionary where keys represent the plane names (e.g., "axial_tumor_slice") and values represent the 
number of tumor-containing slices.

----------------------------  

#### `calculate_position_tumor_slices()`

Return (`dict`): A dictionary containing the minimum and maximum slice indices for each plane 
(e.g., "lower_axial_tumor_slice", "upper_axial_tumor_slice").

----------------------------

#### `calculate_tumor_pixel()`

Return (`dict`): A dictionary where keys represent each tumor label (e.g., "lesion_size_label1") and values represent 
the lesion size in voxels.

----------------------------  

#### `calculate_tumor_distance()`

**Parameters**:

- `brain_centre_mass` (`array-like`): The center of mass of the brain used as a reference point.

Return (`dict`): A dictionary where each key represents the tumor label and the value represents the distance between 
the tumor and the brain's center of mass.

----------------------------  

#### `calculate_tumor_center_mass()`

**Parameters**:

Return (`dict`):  A dictionary where keys represent each plane and label (e.g., "axial_tumor_center_mass") and values 
represent the coordinates of the tumor center of mass.

---------------------------- 

#### `extract_features()`

Returns (`dict`): All tumor features. 

  - Center of mass per label and plane (e.g., "axial_tumor_center_mass").
  - Tumor location relative to brain center of mass.
  - Lesion size per label.
  - Total lesion size.
  - Number of tumor-containing slices per plane.
  - Lower and upper bounds of tumor slices.

----------------------------  


