import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import warnings

import streamlit as st
from PIL import Image

from src.app.util.pages.Home_Page import home_page
from src.app.util.pages.Longitudinal_Measurements import longitudinal
from src.app.util.pages.Model_Performance_Analysis import performance
from src.app.util.pages.Multi_Model_Performance_Comparison import multi_model
from src.app.util.pages.Multivariate_Feature_Analysis import multivariate
from src.app.util.pages.Pairwise_Model_Performance_Comparison import pairwise_comparison
from src.app.util.pages.Segmentation_Error_Matrix import matrix
from src.app.util.pages.Subjects_Exploration import subjects
from src.app.util.pages.Univariate_Feature_Analysis import univariate

warnings.simplefilter(action="ignore", category=FutureWarning)


class AUDIT:
    def __init__(self):
        self.apps = []

    def add_page(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        st.set_page_config(page_title="AUDIT", page_icon=":brain", layout="wide")
        audit_logo = Image.open("./src/app/util/images/AUDIT_transparent.png")
        st.sidebar.image(audit_logo, use_column_width=True)

        st.sidebar.markdown("## Main Menu")
        page = st.sidebar.selectbox("Select Page", self.apps, format_func=lambda page: page["title"])
        st.sidebar.markdown("---")
        page["function"]()


app = AUDIT()
app.add_page("Home Page", home_page)
app.add_page("Univariate Analysis", univariate)
app.add_page("Multivariate Analysis", multivariate)
app.add_page("Segmentation Error Matrix", matrix)
app.add_page("Model Performance Analysis", performance)
app.add_page("Pairwise Model Performance Comparison", pairwise_comparison)
app.add_page("Multi-model Performance Comparison", multi_model)
app.add_page("Longitudinal Measurements", longitudinal)
app.add_page("Subjects Exploration", subjects)

app.run()
