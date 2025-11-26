class ConstantsAPP:
    def __init__(self):
        self.mia_url = "https://www.artorg.unibe.ch/research/mia/index_eng.html"
        self.mlg_url = "https://www.aic.uniovi.es/mlgroup/"
        self.header = ""
        self.sub_header = ""
        self.description = ""
        self.contact = "[Contact us - MIA group](%s)" % self.mia_url


class UnivariatePage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Univariate feature analysis"""
        self.sub_header = """
            **Description**: The univariate analysis mode provides a comprehensive and interactive visualization of single-variable distributions
            derived from MRI sequences or ground truth segmentations. This univariate analysis is essential for those
            users aiming to explore and understand the distribution of individual features in their datasets. The
            dashboard is equipped with interactive controls that allow users to dynamically adjust the visualization
            parameters. Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/univariate/) out for more detailed information.
            """

        self.description_boxplot = """
            The inclusion of a box plots or violin plots offers a summary of the feature's distribution, highlighting key
            statistics such as the median, quartiles, and potential outliers. These types of visualizations complement 
            the histogram and probability distribution, providing additional insights into the data's spread and 
            central tendency. 
            """

        self.description_distribution = """
            The inclusion of histograms or probability distribution plots offers a detailed view of the feature’s 
            underlying distribution, highlighting the frequency or density of data points across defined intervals. 
            These visualizations complement box plots and violin plots by providing a clear representation of the 
            data’s overall shape, including patterns such as skewness, peaks, or multimodal tendencies. By capturing 
            the nuances of the distribution, histograms and probability plots enable researchers to uncover hidden 
            trends and better understand the variability within their datasets.           
        """


# Boxplot: This visualization provides a concise summary of the data’s distribution, showcasing key statistics such as the median, quartiles, and potential outliers. It is particularly effective for comparing multiple groups or datasets, offering a clear view of variability and central tendency.
#
# Violin Plot: Combining the features of a boxplot with a detailed representation of the data's density, the violin plot offers a richer visualization of the distribution's shape. It is especially useful for identifying multimodal distributions or subtle patterns within the dat


class MultivariatePage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Multivariate feature analysis"""
        self.sub_header = """
            **Description**: The multivariate analysis mode allows for an in-depth exploration of the extracted features from
            magnetic resonance images alongside their corresponding ground truth segmentations. This is achieved
            through a bidimensional scatter plot that facilitates the visualization of complex relationships between
            different intrinsic features. Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/multivariate/) out for more detailed information.
            """
        self.description = """
            Each point in the scatter plot represents a single data instance, allowing users to observe how various
            features derived from MRI data distribute across different classes. The scatter plot employs two dimensions
            to plot features against each other. This two-dimensional approach aids in uncovering correlations,
            clusters, and outliers that may not be apparent in a unidimensional analysis. Data points in the scatter
            plot are color-coded to represent different datasets, however, it also allows to color some of the
            features.

            Users can interact with the scatter plot by zooming, panning, and selecting specific data points to obtain
            more detailed information. This interactivity enhances the analytical capabilities, allowing for a more
            thorough investigation of the data.
        """


class SegmentationErrorMatrixPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Segmentation Error Matrix"""
        self.sub_header = """**Description**: Thi analysis mode shows a pseudo-confusion matrix that visualizes the 
        performance of a segmentation model at the pixel level. It summarizes how frequently each ground truth label is 
        misclassified as another class, helping identify common errors across anatomical structures or lesion subregions.
        Unlike a standard confusion matrix, this visualization focuses specifically on misclassifications, correctly 
        segmented pixels (true positives) are not shown. Each row corresponds to a true label, and each column to a 
        predicted label. The matrix is row-normalized, so each row sums to 100%, making it easier to interpret
         class-wise prediction errors. Darker cell colors indicate higher misclassification rates."""

        self.description = """
            - True Label (rows): Actual pixel class from the ground truth segmentation.
            - Predicted Label (columns): Pixel class predicted by the model.
            - Diagonal cells: Not shown. The matrix highlights only errors.
            - Off-diagonal cells: Indicate how often a true label was wrongly predicted as another class.
        
        Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/segmentation_error/) out for more detailed information.
        """


class ModelPerformanceAnalysisPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Model performance analysis"""
        self.sub_header = """
        **Description:** The single model performance analysis mode allows for the exploration of model performance based on features
        extracted from magnetic resonance images and their corresponding ground truth segmentations. The scatter
        plot displayed visualizes the relationship between a feature aggregated (for all labels) or not on the x-axis
        and a metric on the y-axis. On the left sidebar, users can configure the visualization by selecting different
        models and features. Additionally, the aggregated checkbox allows to aggregate the metric over all regions or
        analyze them individually. Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/single_model/) out for more detailed information.
        """

        self.description = """
        Each data point represents a specific subject from one of the available datasets (distinguished by color). The
        colors help in identifying patterns or trends specific to each dataset, potentially revealing variations in
        model performance across different data sources.
        """


class PairwiseModelPerformanceComparisonPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Pairwise model performance comparison"""
        self.sub_header = """
        **Description**: The pairwise model performance analysis mode illustrates the percentage difference in a selected
        metric between two models across various regions for each subject. In this bar chart, each bar represents the
        difference in a selected metric for a specific anatomical region (e.g., Average, NEC, ENH, and EDE), comparing the baseline
        model with the benchmark model. The length of each bar indicates the magnitude of the improvement or decline in
        performance, with longer bars representing larger differences. The green color of the bars indicates the overall
        gain achieved by the benchmark model over the baseline model.

        Additionally, there is a checkbox labeled "Aggregated," which, when checked, aggregates the metric across all
        subjects, providing a summarized view of the model's performance differences. 
        Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/pairwise_model/) out for more detailed information.
        """

        self.description = """
        When comparing the performance of two models, several metrics can be used to quantify the difference: Absolute,
        Relative, and Ratio. A detailed explanation can be found below.

        - **Absolute improvement** measures the direct difference between the performance metrics of two models.

        - **Relative improvement** provides a measure of the difference between two metrics relative to the magnitude
          of the reference metric (typically the value of baseline model).

        - **Improvement Ratio** measures how much better one model is compared to another by directly comparing their
          metric ratio.

        For all the formulas are presented, M represents any of the available metrics (Dice score, accuracy, ...).
        """

        self.absolute_formula = r"""\text{Absolute} = M_{\text{Benchmark model}} - M_{\text{Baseline model}}"""
        self.relative_formula = r"""\text{Relative} = \frac{M_{\text{Benchmark model}} - M_{\text{Baseline model}}}{M_{\text{Baseline model}}}"""
        self.ratio_formula = r"""\text{Ratio} = \frac{M_{\text{Benchmark model}}}{M_{\text{Baseline model}}}"""

        self.colorbar = {"decrease": "#ffbf69", "increase": "#90be6d"}


class MultiModelPerformanceComparisonsPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Multi-model performance comparison"""
        self.sub_header = """
        **Description**: The multi-model performance comparison analysis mode allows users to evaluate and compare a 
        set of segmentation models on a single dataset, across multiple metrics and tumor regions. 
        
        First, the following table summarizes the mean and standard deviation obtained by the selected models
        for a set of metrics. The table provides a comprehensive comparison of different segmentation models across
        various tumor regions. Each row corresponds to a specific combination of region and model, and the columns
        present the performance metrics along with their respective standard deviations.

        There is also a checkbox labeled "Aggregated," which, when checked, aggregates the performance metrics across
        all subjects, providing a summarized view of the model's performance.
        """

        self.description = """
            Additionally, a boxplot is shown to further provide more visual insights about the model performance
            distribution. Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/multi_model/) out for more detailed information. 
        """


class LongitudinalAnalysisPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Longitudinal analysis"""
        self.sub_header = """
        **Description**: This analysis mode allows users to assess the evolution of lesion size over time and to evaluate 
        how well predictions align with ground truth data. The dashboard presents lesion size (in mm³) along the 
        vertical axis and a set of timepoints along the horizontal axis. Two primary curves are displayed:

        - Observed Lesion Size: Represents the actual measured lesion size for a given subject at each timepoint.
        - Predicted Lesion Size: Represents the lesion size estimated by an AI model or predictive algorithm at the same timepoints.

        Between each pair of consecutive timepoints, percentage values are displayed above the 
        solid lines. These values represent the relative growth or shrinkage in lesion size between two timepoints:

        - A positive percentage indicates an increase in lesion size (tumor progression).
        - A negative percentage indicates a decrease in lesion size (tumor regression).

        In addition to analyzing temporal changes, the plot highlights the discrepancy between observed and predicted 
        lesion sizes using dotted vertical blue lines. Each of these dotted lines connects the predicted and observed 
        values at a single timepoint and is annotated with a blue percentage, which quantifies the relative error in 
        lesion size estimation at that time.
        """

        self.description = """       
        Together, these visual elements offer a comprehensive overview of how lesion size changes over time and how 
        well those changes are captured by predictive models. The plot is especially useful for identifying timepoints
        where model predictions deviate significantly from actual measurements, enabling a more nuanced understanding 
        of model performance in a longitudinal context. Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/longitudinal/) out for more detailed information.
        """


class SubjectsExplorationPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Subjects Exploration"""
        self.sub_header = """
            **Description**: This analysis mode provides a comprehensive exploration of the selected subject, offering detailed
            insights across several key dimensions. The features are organized into different categories:
             first order statistical features, second order texture features, spatial features, tumor features, and, if
             available, metadata features. Additionally, it provides insights into the nature of the subject compared 
             to the rest of the dataset. Check the [official documentation](https://caumente.github.io/AUDIT/analysis_modes/subjects_exploration/) out for more detailed information.
            """
        self.description = """
        #####
        ....
        """

        self.features_explanation = """
            - __First-order features__: They are statistical measures derived from the pixel intensity values of an MRI image. These features do not consider the spatial arrangement of the pixels, but rather focus on the intensity distribution itself. Examples include: mean, minimum and maximum intensities, standard deviation, skewness, etc.
            - __Second-order features__: They focus on the texture of the image, which involves the spatial relationship between pixels. That is, a texture is defined by measuring patterns, repetitions, and variations in pixel intensity. Main second-order features include: entropy, correlation, or contrast.
            - __Spatial features__: They refer to geometric properties of objects within the MRI image, such as the spatial resolution of the sequences or the organ position within the image.
            - __Tumor features__: They describe the shape and structure of specific regions, especially abnormal regions such as tumors. For instance, tumor size and tumor location, among others.
            - __Metadata (optional)__: They characterize a dataset, including demographic information, patients' age, gender, or location. This information should have been provided by the user as a mapping file at the time of extracting the features.
            """

        self.iqr_explanation = """
            The Inter Quantile Range (IQR) method for outlier detection is a statistical technique used to identify
            outliers in a dataset. It relies on the spread of the middle 50% of the data, providing a robust measure
            of variability that is not influenced by extreme values. The IQR method is a non-parametric technique
            suitable for a variety of data distributions, including normal, skewed, and even data with heavy
            tails. It does not rely on the assumption of normality, making it a versatile and robust choice for outlier
            detection in many scenario
        """
