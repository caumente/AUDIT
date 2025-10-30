The `TumorFeatures` class computes various tumor-related metrics based on a segmented 3D medical image, such as lesion 
size, tumor center of mass, and tumor location relative to the brain's center of mass.

---

## __Overview__

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

---

## __Methods__

### `__init__`

Constructs all the necessary attributes for the TumorFeatures object.

**Parameters**  

- **segmentation** (`np.ndarray`): A numpy array representing the segmentation of the medical image.  
- **spacing** (`tuple`, optional): The voxel spacing of the image (default is `(1, 1, 1)`).  
- **mapping_names** (`dict`, optional): A dictionary mapping segmentation values to names.  
- **planes** (`list[str]`, optional): The planes (axial, coronal, sagittal) for tumor slice analysis. Defaults to `["axial", "coronal", "sagittal"]`.

---

### `count_tumor_pixels`

Counts the number of pixels for each unique value in the segmentation.

**Returns**  

- `dict`: A dictionary with the counts of each unique value in the segmentation.

---

### `calculate_whole_lesion_size`

Calculates the total lesion size in the segmentation.

**Returns**  

- `dict`: A dictionary containing the lesion size in cubic millimeters.

---

### `get_tumor_center_mass`

Calculates the center of mass for the tumor in the image.

**Parameters**  

- **label** (`int`, optional): The label value of the tumor (default is `None`).

**Returns**  

- `np.ndarray`: The center of mass coordinates adjusted by the voxel spacing.

---

### `get_tumor_slices`

Obtains the slices that contain tumor regions in the axial, coronal, and sagittal planes.

**Returns**  

- `tuple`: A tuple containing three lists, each representing the indices of slices with tumor presence in each plane.

---

### `calculate_tumor_slices`

Calculates the number of tumor-containing slices per plane.

**Returns**  

- `dict`: A dictionary where keys represent each plane (e.g., `"axial_tumor_slices"`) and values represent the number of slices with tumor.

---

### `calculate_position_tumor_slices`

Determines the lower and upper tumor slice indices for each plane.

**Returns**  

- `dict`: A dictionary containing the minimum and maximum slice indices for each plane (e.g., `"lower_axial_tumor_slice"`, `"upper_axial_tumor_slice"`).

---

### `calculate_tumor_pixel`

Computes the number of pixels per tumor label and converts them into volume using voxel spacing.

**Returns**  

- `dict`: A dictionary where keys represent each tumor label (e.g., `"lesion_size_label1"`) and values represent the lesion size in voxels.

---

### `calculate_tumor_distance`

Calculates the Euclidean distance between the tumor center of mass and the brain's center of mass.

**Parameters**  

- **brain_centre_mass** (`array-like`): The center of mass of the brain used as a reference point.

**Returns**  

- `dict`: A dictionary where each key represents the tumor label and the value represents the distance between the tumor and the brain's center of mass.

---

### `calculate_tumor_center_mass`

Calculates the tumor center of mass for each label and plane.

**Returns**  

- `dict`: A dictionary where keys represent each plane and label (e.g., `"axial_tumor_center_mass"`) and values represent the coordinates of the tumor center of mass.

---

### `extract_features`

Extracts all tumor-related features, combining lesion size, center of mass, position, and slice information.

**Returns**  

A dictionary containing all computed tumor features, including:

  - Center of mass per label and plane.  
  - Tumor location relative to brain center of mass.  
  - Lesion size per label.  
  - Total lesion size.  
  - Number of tumor-containing slices per plane.  
  - Lower and upper bounds of tumor slices.

---