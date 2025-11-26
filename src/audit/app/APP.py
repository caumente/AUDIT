import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import warnings
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_theme import st_theme

from audit.app.util.constants.features import Features
from audit.app.util.pages.home_page import HomePage
from audit.app.util.pages.longitudinal import Longitudinal
from audit.app.util.pages.multi_model_performance import MultiModelPerformance
from audit.app.util.pages.multivariate_feature import MultivariateFeature
from audit.app.util.pages.pairwise_model_performance import PairwiseModelPerformance
from audit.app.util.pages.segmentation_error_matrix import SegmentationErrorMatrix
from audit.app.util.pages.single_model_performance import SingleModelPerformance
from audit.app.util.pages.subject_exploration import SubjectsExploration
from audit.app.util.pages.univariate_feature import UnivariateFeature
from audit.utils.internal._config_helpers import load_config_file

warnings.simplefilter(action="ignore", category=FutureWarning)


class AUDIT:
    def __init__(self, config):
        self.config = config
        self.features = Features(config)

        # Instantiate pages
        self.pages = [
            {"title": "Home page", "page": HomePage(config)},
            {"title": "Univariate analysis", "page": UnivariateFeature(config)},
            {"title": "Multivariate analysis", "page": MultivariateFeature(config)},
            {"title": "Segmentation error matrix", "page": SegmentationErrorMatrix(config)},
            {"title": "Single model performance", "page": SingleModelPerformance(config)},
            {"title": "Pairwise model performance", "page": PairwiseModelPerformance(config)},
            {"title": "Multi-model performance", "page": MultiModelPerformance(config)},
            {"title": "Longitudinal analysis", "page": Longitudinal(config)},
            {"title": "Subjects exploration", "page": SubjectsExploration(config)},
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
        theme = st_theme(key="app_theme")
        if theme is not None and theme.get("base", None) == "dark":
            audit_logo_path = base_dir / "util/images/AUDIT_DM_transparent.png"

        # Load and display the logo
        if audit_logo_path.exists():
            audit_logo = Image.open(audit_logo_path)
            st.sidebar.image(audit_logo, use_container_width=True)
        else:
            st.sidebar.error(f"Logo not found: {audit_logo_path}")

        st.sidebar.markdown("## Main Menu")

        # Sidebar for selecting pages
        selected_page = st.sidebar.selectbox("Select Page", self.pages, format_func=lambda page: page["title"])
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
