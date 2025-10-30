The `SpatialFeatures` class is designed to compute spatial properties related to 3D medical imaging sequences, such as 
brain MRI scans. This class focuses on calculating basic spatial features like the brain's center of mass and the 
dimensionality of the scan in various planes.

---

## __Overview__

This class is intended to provide spatial insights from a 3D sequence of medical images. It helps to extract two key 
metrics: The center of mass for the brain, which is calculated based on the sequence, and the dimensions of the sequence in
the axial, coronal, and sagittal planes. These spatial features are essential in understanding the brain's structure 
and alignment in a 3D scan, aiding in medical analysis and further processing of brain images.

The following spatial features are available:

- **Brain Center of Mass**: The 3D coordinates of the brain's center, adjusted by voxel spacing.  
- **Sequence Dimensions**: The dimensions of the sequence in the axial, coronal, and sagittal planes.

---

## __Methods__

### `__init__`

Constructs all the necessary attributes for the SpatialFeatures object.

**Parameters**  

- **sequence** (`np.ndarray`): A 3D NumPy array representing the medical image sequence.  
- **spacing** (`np.ndarray`, optional): A tuple representing the voxel spacing of the medical image. Defaults to `(1, 1, 1)`.

---

### `calculate_anatomical_center_mass`

Calculates the center of mass for the anatomical image.

**Returns**  

- `dict`: A dictionary containing the 3D coordinates of the brain's center of mass for each plane (axial, coronal, sagittal), adjusted by the voxel spacing.

---

### `get_shape`

Gets the dimensions of the sequence in axial, coronal, and sagittal planes.

**Returns**  

- `dict`: A dictionary containing the dimensions of the sequence:  
  - `axial_plane_resolution`: Axial plane resolution.  
  - `coronal_plane_resolution`: Coronal plane resolution.  
  - `sagittal_plane_resolution`: Sagittal plane resolution.

---

### `extract_features`

Extracts all spatial features from the sequence.

**Returns**  

A dictionary containing all spatial features, including dimensions and center of mass for each plane.

---