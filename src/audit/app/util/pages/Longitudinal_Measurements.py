import pandas as pd
import streamlit as st

from audit.app.util.pages.BasePage import BasePage
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.sidebars import setup_sidebar_longitudinal_subject
from audit.app.util.commons.sidebars import setup_sidebar_single_dataset
from audit.app.util.commons.sidebars import setup_sidebar_single_model
from audit.app.util.commons.utils import download_longitudinal_plot
from audit.app.util.constants.descriptions import LongitudinalAnalysisPage
from audit.utils.commons.file_manager import read_datasets_from_dict
from audit.visualization.time_series import plot_longitudinal_lesions


class LongitudinalMeasurements(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = LongitudinalAnalysisPage()

    def run(self):
        features_paths = self.config.get("features")
        metrics_paths = self.config.get("metrics")

        # Define page layout
        st.header(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        # Reading feature data
        features_df = read_datasets_from_dict(features_paths)
        metrics_df = read_datasets_from_dict(metrics_paths)
        merged = self.merge_features_metrics(features_df, metrics_df)

        if not merged.empty:
            # Sidebar setup
            selected_set, selected_model = self.setup_sidebar(merged)
            df = processing_data(
                data=merged,
                sets=selected_set,
                models=selected_model,
                features=["ID", "set", "longitudinal_id", "time_point", "lesion_size_whole", "lesion_size_pred"]
            )

            # filter subject
            df['longitudinal_id'] = df['longitudinal_id'].apply(self.clean_longitudinal_id)
            selected_subject = setup_sidebar_longitudinal_subject(df)
            df = df[df.longitudinal_id == selected_subject]

            # Main functionality
            self.plot_visualization(df)
        else:
            st.error("Metric datasets must contain tumor size variable", icon="🚨")

    @staticmethod
    def setup_sidebar(data):

        with st.sidebar:
            st.header("Configuration")

            # Select datasets
            selected_set = setup_sidebar_single_dataset(data)
            selected_model = setup_sidebar_single_model(data)

            return selected_set, selected_model

    @staticmethod
    def merge_features_metrics(features_df, metrics_df):
        features_df = features_df.loc[~features_df['longitudinal_id'].isna(), :]
        if "SIZE" in metrics_df.columns:
            metrics_df = metrics_df.groupby(["ID", "model", "set"])["SIZE"].sum().reset_index().rename(columns={"SIZE": "lesion_size_pred"})
        elif "lesion_size_pred" in metrics_df.columns:
            metrics_df = metrics_df.groupby(["ID", "model", "set"])["lesion_size_pred"].sum().reset_index()
        else:
            return pd.DataFrame()
        # metrics_df = metrics_df.groupby(["ID", "model", "set"])["lesion_size_pred"].sum().reset_index()
        merged = metrics_df.merge(features_df, on=["ID", "set"])

        return merged

    @staticmethod
    def clean_longitudinal_id(value):
        value_str = str(value)

        if value_str.endswith('.0'):
            return value_str[:-2]

        return value_str

    def plot_visualization(self, data):
        data = data.reset_index(drop=True)

        st.markdown(self.descriptions.description)
        fig = plot_longitudinal_lesions(data)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True, scrolling=True)
        download_longitudinal_plot(fig, label="longitudinal analysis", filename="longitudinal_analysis")
