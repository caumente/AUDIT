[//]: # (::: src.feature_extractor)


This `feature extraction` pipeline is designed to process medical imaging datasets, specifically MRI scans, to extract a 
wide range of features including spatial, tumor-related, statistical, and texture-based characteristics. The pipeline 
is composed of two core components: the feature_extractor.py script, which orchestrates the entire process, and the 
underlying feature extraction logic contained in src.features.main.py.

The pipeline operates as follows:

- **Configuration and Logging**: The process begins by loading configuration settings from a YAML file, specifying data 
paths, features to extract, and output directories. A logging system is set up to monitor and record the progress of 
the feature extraction.

- **Dataset Processing**: For each dataset defined in the configuration, the pipeline iterates over all subject data, 
extracting features from MRI sequences and associated segmentations. This is handled by the extract_features function,
which computes various features such as spatial dimensions, tumor characteristics, statistical metrics, and texture 
properties of the images.

- **Feature Extraction**: The pipeline uses specialized classes for different types of features:

    - Spatial Features: Related to image dimensions and brain structure.
    - Tumor Features: Derived from segmentations to describe the tumor’s shape, volume, and position.
    - Statistical Features: First-order statistics like mean, variance, etc., extracted from image sequences.
    - Texture Features: Second-order metrics describing the texture patterns in the images.

If longitudinal data is present, the pipeline also extracts and includes time-point and longitudinal 
identifiers for further analysis.

- **Data Output**: Once features are extracted for each subject, they are compiled into a DataFrame, which is saved as 
a CSV file. 

This pipeline provides an automated and extensible framework for processing large-scale MRI datasets, ensuring that 
all relevant features are extracted and saved for downstream analysis, such as predictive modeling or visualization.

In the following sections, the users can explore in detail the different methods provided by AUDIT to extract relevant 
information from MRIs.
