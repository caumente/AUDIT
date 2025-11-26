import pandas as pd
import streamlit as st
from streamlit_theme import st_theme

from audit.app.util.commons.checks import none_check
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.utils import download_longitudinal_plot
from audit.app.util.constants.descriptions import LongitudinalAnalysisPage
from audit.app.util.pages.base_page import BasePage
from audit.utils.internal._csv_helpers import read_datasets_from_dict
from audit.visualization.commons import update_longitudinal_plot
from audit.visualization.time_series import plot_longitudinal_lesions


class Longitudinal(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = LongitudinalAnalysisPage()

    def run(self):
        theme = st_theme(key="univariate_theme")
        if theme is not None:
            self.template = theme.get("base")

        features_paths = self.config.get("features")
        metrics_paths = self.config.get("metrics")

        # Define page layout
        st.header(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        proceed = none_check(metrics_paths=metrics_paths, features_paths=features_paths)
        if proceed[0]:
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
                    features=["ID", "set", "longitudinal_id", "time_point", "lesion_size_whole", "lesion_size_pred"],
                )

                # filter subject
                df["longitudinal_id"] = df["longitudinal_id"].apply(self.clean_longitudinal_id)
                selected_subject = self.sidebar.setup_sidebar_longitudinal_subject(df)
                df = df[df.longitudinal_id == selected_subject]

                # Main functionality
                self.plot_visualization(df)
            else:
                st.error("Metric datasets must contain tumor size variable", icon="🚨")
        else:
            st.error(proceed[-1], icon="🚨")

    def setup_sidebar(self, data):
        with st.sidebar:
            st.header("Configuration")

            # Select datasets
            selected_set = self.sidebar.setup_sidebar_single_dataset(data)
            selected_model = self.sidebar.setup_sidebar_single_model(data)

            return selected_set, selected_model

    @staticmethod
    def merge_features_metrics(features_df, metrics_df):
        features_df = features_df.loc[~features_df["longitudinal_id"].isna(), :]
        if "SIZE" in metrics_df.columns:
            metrics_df = (
                metrics_df.groupby(["ID", "model", "set"])["SIZE"]
                .sum()
                .reset_index()
                .rename(columns={"SIZE": "lesion_size_pred"})
            )
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

        if value_str.endswith(".0"):
            return int(value_str[:-2])

        return value_str

    def plot_visualization(self, data):
        data = data.reset_index(drop=True)

        st.markdown(self.descriptions.description)
        col1, col2 = st.columns([1, 1], gap="small")
        with col2:
            customization_longitudinal = st.selectbox(
                label="Customize visualization",
                options=["Standard visualization", "Custom visualization"],
                index=0,
                key="longitudinal",
            )

        if customization_longitudinal == "Custom visualization":
            self.render_longitudinal_analysis_with_customization(data)
        else:
            self.render_longitudinal_analysis(data)

    def render_longitudinal_analysis(self, data):
        fig = plot_longitudinal_lesions(data, template=self.template)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True, scrolling=True)
        download_longitudinal_plot(fig, label="longitudinal analysis", filename="longitudinal_analysis")

    def render_longitudinal_analysis_with_customization(self, data):
        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

        # Column 1: Display the plot
        with col1:
            fig = plot_longitudinal_lesions(data, template=self.template)
        with col2:
            update_longitudinal_plot(fig, key="longitudinal")

        with col1:
            st.plotly_chart(fig, theme="streamlit", use_container_width=True, scrolling=True)
            download_longitudinal_plot(fig, label="longitudinal analysis", filename="longitudinal_analysis")
