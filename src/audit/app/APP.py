import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import warnings
from pathlib import Path
import streamlit as st
from PIL import Image

from audit.utils.commons.file_manager import load_config_file
from audit.app.util.pages.Home_Page import home_page
from audit.app.util.pages.Longitudinal_Measurements import longitudinal
from audit.app.util.pages.Model_Performance_Analysis import performance
from audit.app.util.pages.Multi_Model_Performance_Comparison import multi_model
from audit.app.util.pages.Multivariate_Feature_Analysis import multivariate
from audit.app.util.pages.Pairwise_Model_Performance_Comparison import pairwise_comparison
from audit.app.util.pages.Segmentation_Error_Matrix import matrix
from audit.app.util.pages.Subjects_Exploration import subjects
from audit.app.util.pages.Univariate_Feature_Analysis import univariate

warnings.simplefilter(action="ignore", category=FutureWarning)


class AUDIT:
    def __init__(self, config):
        self.pages = [
            {"title": "Home Page", "function": home_page},
            {"title": "Univariate Analysis", "function": univariate},
            {"title": "Multivariate Analysis", "function": multivariate},
            {"title": "Segmentation Error Matrix", "function": matrix},
            {"title": "Model Performance Analysis", "function": performance},
            {"title": "Pairwise Model Performance Comparison", "function": pairwise_comparison},
            {"title": "Multi-model Performance Comparison", "function": multi_model},
            {"title": "Longitudinal Measurements", "function": longitudinal},
            {"title": "Subjects Exploration", "function": subjects}
        ]
        self.config = config

    def add_page(self, title, func):
        self.pages.append({"title": title, "function": func})

    def run(self):
        st.set_page_config(page_title="AUDIT", page_icon=":brain", layout="wide")

        # Resolve the absolute path for the logo
        base_dir = Path(__file__).resolve().parent
        audit_logo_path = base_dir / "util/images/AUDIT_transparent.png"

        # Load the image
        if audit_logo_path.exists():
            audit_logo = Image.open(audit_logo_path)
            # st.sidebar.image(audit_logo, use_column_width=True)
            st.sidebar.image(audit_logo, use_container_width=True)
        else:
            st.sidebar.error(f"Logo not found: {audit_logo_path}")

        st.sidebar.markdown("## Main Menu")
        page = st.sidebar.selectbox("Select Page", self.pages, format_func=lambda page: page["title"])
        st.sidebar.markdown("---")
        page["function"](self.config)


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
