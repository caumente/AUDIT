[//]: # (::: src.features.statistical.StatisticalFeatures)


The `StatisticalFeatures` class provides a convenient way to compute several common statistical metrics from a given
array of data.

### Overview

The class utilizes **NumPy** for efficient numerical operations and **SciPy** for computing first-order statistical
features. By encapsulating these features in a class, users can easily compute various statistical
properties of a dataset with minimal boilerplate code.

The following statistical features are available:

- **Maximum intensity**: The highest value in the MRI.
- **Minimum intensity**: The lowest value in the MRI.
- **Mean intensity**: The average value of the MRI.
- **Median intensity**: The middle value of the MRI when sorted.
- **Standard deviation intensity**: A measure of the amount of variation or dispersion of the values.
- **Range intensity**: The difference between the maximum and minimum values.
- **Skewness**: A measure of the asymmetry of the distribution of pixel values.

### Methods

#### `__init__()`

**Description**:  
The constructor method initializes the `StatisticalFeatures` object by accepting a 3D magnetic resonance image in the
form of a NumPy array. Once initialized, the class provides several methods to compute various statistical features from
the MRI. Notice that, given the background of MRI images usually is equal to 0, those values should be removed to not
interfere with the computations.

**Parameters**:

- `sequence` (`np.ndarray`): A 3D MRI in form of NumPy array from which statistical features will be calculated.

----------------------------  

#### `get_max_intensity()`

Returns (`float`): The maximum intensity value in the MRI.

----------------------------  

#### `get_min_intensity()`

Returns (`float`): The minimum intensity value in the MRI.

----------------------------  

#### `get_mean_intensity()`

Returns (`float`): The mean intensity value in the MRI.  

----------------------------  

#### `get_median_intensity()`

Returns (`float`): The median intensity value in the MRI.

----------------------------  

#### `get_std_intensity()`

Returns (`float`): The standard deviation of the of intensity values in the MRI.

----------------------------  

#### `get_range_intensity()`

Returns (`float`): the range of intensity values in the MRI (i.e., the difference between the maximum and minimum values).

----------------------------  

#### `get_skewness()`

Returns (`float`): The skewness of the intensity values in the MRI, a measure of asymmetry in the distribution.

----------------------------  

#### `extract_features()`

Returns (`dict`): All statistical features. 

  - `max_intensity`: Maximum intensity value in the MRI.
  - `min_intensity`: Minimum intensity value in the MRI.
  - `mean_intensity`: Mean intensity value in the MRI.
  - `median_intensity`: Median intensity value in the MRI.
  - `std_intensity`: Standard deviation of intensity values in the MRI.
  - `range_intensity`: Range of intensity values in the MRI.
  - `skewness`: Skewness of the intensity values in the MRI.

----------------------------  


