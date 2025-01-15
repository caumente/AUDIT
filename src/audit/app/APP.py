import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import warnings
from pathlib import Path
import streamlit as st
from PIL import Image

from audit.utils.commons.file_manager import load_config_file
from audit.app.util.pages.Home_Page import HomePage
from audit.app.util.pages.Longitudinal_Measurements import LongitudinalMeasurements
from audit.app.util.pages.Model_Performance_Analysis import ModelPerformanceAnalysis
from audit.app.util.pages.Multi_Model_Performance_Comparison import MultiModelPerformanceComparison
from audit.app.util.pages.Multivariate_Feature_Analysis import MultivariateFeatureAnalysis
from audit.app.util.pages.Pairwise_Model_Performance_Comparison import PairwiseModelPerformanceComparison
from audit.app.util.pages.Segmentation_Error_Matrix import SegmentationErrorMatrix
from audit.app.util.pages.Subjects_Exploration import SubjectsExploration
from audit.app.util.pages.Univariate_Feature_Analysis import UnivariateFeatureAnalysis
from audit.app.util.constants.features import Features

warnings.simplefilter(action="ignore", category=FutureWarning)


class AUDIT:
    def __init__(self, config):
        self.config = config
        self.features = Features(config)

        # Instantiate pages
        self.pages = [
            {"title": "Home Page", "page": HomePage(config)},
            {"title": "Univariate Analysis", "page": UnivariateFeatureAnalysis(config)},
            {"title": "Multivariate Analysis", "page": MultivariateFeatureAnalysis(config)},
            {"title": "Segmentation Error Matrix", "page": SegmentationErrorMatrix(config)},
            {"title": "Model Performance Analysis", "page": ModelPerformanceAnalysis(config)},
            {"title": "Pairwise Model Performance Comparison", "page": PairwiseModelPerformanceComparison(config)},
            {"title": "Multi-model Performance Comparison", "page": MultiModelPerformanceComparison(config)},
            {"title": "Longitudinal Measurements", "page": LongitudinalMeasurements(config)},
            {"title": "Subjects Exploration", "page": SubjectsExploration(config)}
        ]

    def add_page(self, title, page_instance):
        """
        Adds a new page to the application.
        Args:
            title (str): Title of the page to be displayed in the sidebar.
            page_instance (BasePage): Instance of the page class.
        """
        self.pages.append({"title": title, "page": page_instance})

    def run(self):
        """
        Main function to run the Streamlit app.
        """
        st.set_page_config(page_title="AUDIT", page_icon=":brain", layout="wide")

        # Resolve the absolute path for the logo
        base_dir = Path(__file__).resolve().parent
        audit_logo_path = base_dir / "util/images/AUDIT_transparent.png"

        # Load and display the logo
        if audit_logo_path.exists():
            audit_logo = Image.open(audit_logo_path)
            st.sidebar.image(audit_logo, use_container_width=True)
        else:
            st.sidebar.error(f"Logo not found: {audit_logo_path}")

        st.sidebar.markdown("## Main Menu")

        # Sidebar for selecting pages
        selected_page = st.sidebar.selectbox(
            "Select Page",
            self.pages,
            format_func=lambda page: page["title"]
        )
        st.sidebar.markdown("---")

        # Run the selected page
        selected_page["page"].run()


def main():
    # Extract the config path from sys.argv (Streamlit passes arguments this way)
    config_path = "./configs/app.yml"  # Default config path
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        config_path = sys.argv[2]

    # Load the configuration file
    config = load_config_file(config_path)

    # Initialize and run the app
    app = AUDIT(config)
    app.run()


if __name__ == "__main__":
    main()
