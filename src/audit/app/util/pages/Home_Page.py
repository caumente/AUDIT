"""
  Copyright 2024 Carlos Aumente Maestro

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

import streamlit as st
from PIL import Image
from pathlib import Path


def home_page(config):

    # Load images
    # audit_logo = Image.open("./audit/app/util/images/AUDIT.png")
    # audit_schema = Image.open("./audit/app/util/images/audit_schema.png")
    audit_logo = Image.open(Path(__file__).parent.parent / "images/AUDIT_transparent.png")
    audit_schema = Image.open(Path(__file__).parent.parent / "images/audit_schema.png")

    # Title and description
    left_col, right_col = st.columns([2, 1])
    left_col.title("Welcome to AUDIT")
    left_col.markdown(
        """
        <h3>An open-source Python library for comprehensive evaluation of segmentation models and medical image analysis</h3>
        <p style="margin: 5px 0;"><b>Created by Carlos Aumente Maestro</b></p>
        <p style="margin: 5px 0;"><b>Artificial Intelligence Center, University of Oviedo</b></p>
        <p style="margin: 5px 0;"><b>ARTORG - Center for Biomedical Engineering Research, University of Bern</b></p>
    """,
        unsafe_allow_html=True,
    )
    right_col.image(audit_logo, output_format="PNG")

    # Summary secction
    st.markdown("---")
    st.header("""Summary""")
    st.write("""
    AUDIT, Analysis & evalUation Dashboard of artIficial inTelligence, is a tool designed to provide
    researcher and developers an interactive way to better analyze and explore MRI datasets and segmentation models.
    Given its functionalities to extract the most relevant features and metrics from your several data sources, it
    allows for uncovering biases both intra and inter-dataset as well as within the model predictions. Some of the main
    capabilities of AUDIT are presented below:""")

    st.markdown("""
        - **Data management**: Easily work and preprocess MRIs from various sources.
        - **Feature extraction**: Extract relevant features from the images and their segmentations for analysis.
        - **Model robustness**: Assess model generalization by evaluating its performance across severa experiments
                                and conditions.
        - **Bias detection**: Identify potential biases either in model predictions and performance or on your data.
        - **Longitudinal analysis**: Track the model performance over different time points.
        - **High compatibility**: Provides connection with tools like ITK-SNAP and other external tools.
    """)

    # st.markdown("""
    # Details of our work are provided in the  paper. We encourage researchers and developers to use AUDIT to gain
    # insights....
    # """)

    # Usage seccion
    st.image(audit_schema, output_format="PNG")
    st.header("""Usage""")
    st.markdown(
        """
        - **Home Page**: The main landing page of the tool.
        - **Univariate Analysis**: Exploration of individual variables to understand their distributions and discover
                                    outliers in it.
        - **Multivariate Analysis**: Examination of multiple variables simultaneously to explore relationships and
                                     hidden patterns.
        - **Segmentation Error Matrix**: A pseudo-confusion matrix displaying the errors associated with the
                                         segmentation tasks.
        - **Model Performance Analysis**: Evaluation of the effectiveness and accuracy of a single model.
        - **Pairwise Model Performance Comparison**: Perform pair-wise comparisons between models to find statistical
                                                     significant differences.
        - **Multi-model Performance Comparison**: Comparative analysis of performance metrics across multiple models.
        - **Longitudinal Measurements**: Analysis of data collected over time to observe trends and changes on model
                                         accuracy.
        - **Subjects Exploration**: Detailed examination of individual subjects within the dataset.
        """
    )
    st.markdown("---")

    # Contact information seccion
    left_info_col, right_info_col = st.columns(2)
    left_info_col.markdown(
        """
        ## Authors

        ##### Carlos Aumente
        - Email: <UO297103@uniovi.es>
        - GitHub: https://github.com/caumente/

        ##### Mauricio Reyes
        ##### Michael Müller
        ##### Jorge Diez
        ##### Beatriz Remeseiro

        Please feel free to contact us with any issues, comments, or questions. [Contact Us](UO297103@uniovi.es)
        """,
        unsafe_allow_html=True,
    )

    right_info_col.markdown(
        """
        ### License
        [Under Apache License 2.0](https://github.com/caumente/AUDIT/blob/main/LICENSE.md)
        """
    )
    right_info_col.markdown(
        """
        ### Documentation
        [Documentation](https://caumente.github.io/AUDIT/)
         """
    )
    right_info_col.markdown(
        """
        ### Code repository
        [GitHub Repository](https://github.com/caumente/AUDIT/)

        """
    )

    # The footer
    st.markdown("---")
    st.write("© 2024 AUDIT project")
