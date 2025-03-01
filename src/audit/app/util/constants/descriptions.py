from audit.app.util.constants.features import Features


class ConstantsAPP:
    def __init__(self):
        self.mia_url = "https://www.artorg.unibe.ch/research/mia/index_eng.html"
        self.mlg_url = "https://www.aic.uniovi.es/mlgroup/"
        self.header = ""
        self.sub_header = ""
        self.description = ""
        self.contact = "[Contact us - MIA group](%s)" % self.mia_url
        # self.features = Features()


class UnivariatePage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Univariate feature analysis"""
        self.sub_header = """
            **Description**: It provides a comprehensive and interactive visualization of single-variable distributions
            derived from MRI sequences or ground truth segmentations. This univariate analysis is essential for those
            users aiming to explore and understand the distribution of individual features in their datasets. The
            dashboard is equipped with interactive controls that allow users to dynamically adjust the visualization
            parameters.
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
            **Description**: The following figure allows for an in-depth exploration of the extracted features from
            magnetic resonance images (MRI) alongside their corresponding ground truth segmentations. This is achieved
            through a bidimensional scatter plot that facilitates the visualization of complex relationships between
            different intrinsic features.
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
        self.sub_header = """**Description**: The figure below is a confusion matrix that visualizes the performance
        of an AI segmentation model in labeling MRI image pixels. Each row represents the actual pixel class as labeled
        by a neuro-radiologist, while each column represents the predicted pixel class by the AI model. The numbers in
        the cells indicate the count/percentage of pixels for each actual-predicted class pair. A darker cell color
        signifies a higher number of errors, highlighting the model's misclassifications."""

        self.description = """
        - **True Label**: Indicated along the rows, representing the actual pixel classifications.
        - **Predicted Label**: Indicated along the columns, representing the AI model's pixel classifications.
        - **Diagonal Cells**: Correct classifications where the predicted label matches the true label.
        - **Off-Diagonal Cells**: Misclassifications where the predicted label differs from the true label.
        """


class ModelPerformanceAnalysisPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Model performance analysis"""
        self.sub_header = """
        **Description:** The following figure allows for the exploration of model performance based on features
        extracted from magnetic resonance images (MRI) and their corresponding ground truth segmentations. The scatter
        plot displayed visualizes the relationship between a feature aggregated (for all labels) or not on the x-axis
        and a metric on the y-axis. On the left sidebar, users can configure the visualization by selecting different
        models and features. Additionally, the aggregated checkbox allows to aggregate the metric over all regions or
        analyze them individually
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
        **Description**: The following figure illustrates the percentage difference in a selected
        metric between two models across various regions for each subject. In this bar chart, each bar represents the
        difference in a selected metric for a specific brain region (Average, NEC, ENH, and EDE), comparing the baseline
        model with the benchmark model. The length of each bar indicates the magnitude of the improvement or decline in
        performance, with longer bars representing larger differences. The green color of the bars indicates the overall
        gain achieved by the benchmark model over the baseline model.

        Additionally, there is a checkbox labeled "Aggregated," which, when checked, aggregates the metric across all
        subjects, providing a summarized view of the model's performance differences.
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
        self.relative_formula = (
            r"""\text{Relative} = \frac{M_{\text{Benchmark model}} - M_{\text{Baseline model}}}{M_{\text{Baseline model}}}"""
        )
        self.ratio_formula = r"""\text{Ratio} = \frac{M_{\text{Benchmark model}}}{M_{\text{Baseline model}}}"""

        self.colorbar = {"decrease": "#ffbf69", "increase": "#90be6d"}


class MultiModelPerformanceComparisonsPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Multi-model performance comparison"""
        self.sub_header = """
        **Description**: The following table summarizes the mean and standard deviation obtained by the selected models
        for a set of metrics. The table provides a comprehensive comparison of different segmentation models across
        various tumor regions. Each row corresponds to a specific combination of region and model, and the columns
        present the performance metrics along with their respective standard deviations.

        There is also a checkbox labeled "Aggregated," which, when checked, aggregates the performance metrics across
        all subjects, providing a summarized view of the model's performance.
        """

        self.description = """
            Additionally, a boxplot is shown to further provide more visual insights about the model performance
            distribution.
        """


class LongitudinalAnalysisPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Longitudinal analysis"""
        self.sub_header = """
            **Description**: The following figures allow visualization of longitudinal data depicting the variation in
            lesion size over time. Both lineplots are designed to provide insights into how well predicted lesion
            sizes align with actual values over the course of multiple time points. Users can interact with the plot by
            zooming, panning, and selecting specific data points to obtain more detailed information. This interactivity
            enhances the analytical capabilities, allowing for a more thorough investigation of the data.


        ##### Relative Error in Lesion Size Estimation
        This plot shows two lines representing actual lesion size and predicted lesion size over different time points.
        Dashed lines between data points indicate the relative error in the lesion size estimation, displayed as a
        percentage above each segment. Additionally, annotations highlight the percentage difference between actual
        and predicted lesion sizes.

            """
        self.description = """
        ##### Absolute Difference in Lesion Size Variation
        This plot displays the absolute difference in variation between actual and predicted lesion sizes over different
        time points. Slopes between consecutive points indicate the absolute difference in variation, annotated with
        numerical values. Each line is color-coded to differentiate between observed and predicted lesion sizes.
        """


class SubjectsExplorationPage(ConstantsAPP):
    def __init__(self):
        super().__init__()

        self.header = """Subjects Exploration"""
        self.sub_header = """
            **Description**: This tab provides a comprehensive exploration of the selected subject, offering detailed
            insights across several key dimensions. The features are organized into three primary categories: anatomical
             features, first order statistical features, and second order texture features. Additionally, it provides
             insights into the nature of the subject compared to the rest of the dataset.
            """
        self.description = """
        #####
        ....
        """

        self.features_explanation = """
            - Anatomical features refer to the structural characteristics of biological entities. This category includes
            details about the physical structure, shape, size, and spatial arrangement of tumors.
    
            - Statistical features involve numerical attributes derived from MRI quantitative measurements. These features
             are used to describe the distribution, variability, etc.
    
            - Texture features describe patterns and variations within an MRI. These features capture details about the
            surface characteristics, smoothness, roughness, that are visually discernible but not necessarily related to
            intensity.
            """

        self.iqr_explanation = """
            The Inter Quantile Range (IQR) method for outlier detection is a statistical technique used to identify
            outliers in a dataset. It relies on the spread of the middle 50% of the data, providing a robust measure
            of variability that is not influenced by extreme values. The IQR method is a non-parametric technique
            suitable for a variety of data distributions, including normal, skewed, and even data with heavy
            tails. It does not rely on the assumption of normality, making it a versatile and robust choice for outlier
            detection in many scenario
        """