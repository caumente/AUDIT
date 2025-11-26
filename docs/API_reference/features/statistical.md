The `StatisticalFeatures` class provides a convenient way to compute several common statistical metrics from a given
array of data.

---

## __Overview__

This class utilizes **NumPy** for efficient numerical operations and **SciPy** for computing first-order statistical
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
- **Kurtosis**: A measure of the "tailedness" of the intensity distribution.

---

## __Methods__

### `__init__`

Constructs all the necessary attributes for the StatisticalFeatures object.

**Parameters**  

- **sequence** (`np.ndarray`): A 3D NumPy array representing the MRI sequence from which statistical features are to be computed.

---

### `get_max_intensity`

Computes the maximum intensity value in the sequence.

**Returns**  

- `float`: The maximum intensity value in the sequence.

---

### `get_min_intensity`

Computes the minimum intensity value in the sequence.

**Returns**  

- `float`: The minimum intensity value in the sequence.

---

### `get_mean_intensity`

Computes the mean intensity value in the sequence.

**Returns**  

- `float`: The mean intensity value in the sequence.

---

### `get_median_intensity`

Computes the median intensity value in the sequence.

**Returns**  

- `float`: The median intensity value in the sequence.

---

### `get_percentile_n`

Computes the n-th percentile of the intensity values in the sequence.

**Parameters**  

- **n** (`float`): The percentile value to compute (e.g., `10` or `90`).

**Returns**  

- `float`: The computed n-th percentile intensity.

---

### `get_std_intensity`

Computes the standard deviation of intensity values in the sequence.

**Returns**  

- `float`: The standard deviation of intensity values.

---

### `get_range_intensity`

Computes the range of intensity values in the sequence (max - min).

**Returns**  

- `float`: The range of intensity values in the sequence.

---

### `get_skewness`

Computes the skewness of the intensity values in the sequence.

**Returns**  

- `float`: The skewness of the intensity distribution.

---

### `get_kurtosis`

Computes the kurtosis of the intensity values in the sequence.

**Returns**  

- `float`: The kurtosis of the intensity distribution.

---

### `extract_features`

Computes and returns all statistical metrics as a dictionary.

**Returns**  

A dictionary containing the following statistical metrics:

  - `max_intensity`: Maximum intensity value in the MRI.  
  - `min_intensity`: Minimum intensity value in the MRI.  
  - `mean_intensity`: Mean intensity value in the MRI.  
  - `median_intensity`: Median intensity value in the MRI.  
  - `10th_percentile_intensity`: 10th percentile intensity.  
  - `90th_percentile_intensity`: 90th percentile intensity.  
  - `std_intensity`: Standard deviation of intensity values.  
  - `range_intensity`: Range of intensity values.  
  - `skewness`: Skewness of the intensity values.  
  - `kurtosis`: Kurtosis of the intensity values.

---