import pandas as pd
import streamlit as st
from streamlit_plotly_events import plotly_events
from streamlit_theme import st_theme

from audit.app.util.commons.checks import dataset_sanity_check
from audit.app.util.commons.checks import none_check
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import ModelPerformanceAnalysisPage
from audit.app.util.constants.metrics import Metrics
from audit.app.util.pages.base_page import BasePage
from audit.utils.commons.strings import pretty_string
from audit.utils.internal._csv_helpers import read_datasets_from_dict
from audit.visualization.commons import update_plot_customization
from audit.visualization.scatter_plots import multivariate_metric_feature


class SingleModelPerformance(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = ModelPerformanceAnalysisPage()
        self.metrics = Metrics().get_metrics()

    def run(self):
        theme = st_theme(key="single_model_theme")
        if theme is not None:
            self.template = theme.get("base")

        # Load configuration file
        metrics_paths = self.config.get("metrics")
        features_paths = self.config.get("features")

        # Define page
        st.subheader(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        proceed = none_check(metrics_paths=metrics_paths, features_paths=features_paths)
        if proceed[0]:
            # Load the data
            features_df = read_datasets_from_dict(features_paths)
            metrics_df = read_datasets_from_dict(metrics_paths)

            col1, col2 = st.columns([2, 2], gap="small")
            with col1:
                agg = self.sidebar.setup_aggregation_button()
                st.markdown("**Double click on a point to highlight it in red and then visualize it disaggregated.**")
            with col2:
                customization_scatter = st.selectbox(
                    label="Customize visualization",
                    options=["Standard visualization", "Custom visualization"],
                    index=0,
                    key="single_model",
                )
            merged_data = self.merge_features_and_metrics(features=features_df, metrics=metrics_df, aggregate=agg)

            # Setup sidebar
            selected_sets, selected_model, feature, metric, selected_regions = self.setup_sidebar(
                data=merged_data, data_paths=metrics_paths, aggregated=agg
            )
            if not dataset_sanity_check(selected_sets):
                st.error("Please, select a dataset from the left sidebar", icon="🚨")
            else:
                df = processing_data(
                    merged_data,
                    sets=selected_sets,
                    models=selected_model,
                    regions=selected_regions,
                    features=["ID", "model", feature, self.metrics.get(metric, None), "set", "region"],
                )
                self.scatter_plot_logic(
                    data=df, x_axis=feature, y_axis=metric, aggregated=agg, customization=customization_scatter
                )

                st.markdown(self.descriptions.description)
        else:
            st.error(proceed[-1], icon="🚨")

    def setup_sidebar(self, data, data_paths, aggregated):
        with st.sidebar:
            st.header("Configuration")

            selected_set = self.sidebar.setup_sidebar_multi_datasets(data_paths)
            selected_model = self.sidebar.setup_sidebar_single_model(data)
            selected_y_axis = self.sidebar.setup_sidebar_single_metric(data)
            selected_x_axis = self.sidebar.setup_sidebar_features(data, name="Feature")
            selected_regions = self.sidebar.setup_sidebar_regions(data, aggregated)

        return selected_set, selected_model, selected_x_axis, selected_y_axis, selected_regions

    @staticmethod
    def merge_features_and_metrics(features: pd.DataFrame, metrics: pd.DataFrame, aggregate=True) -> pd.DataFrame:
        # Aggregate metrics by ID, model, and set (optionally including region)
        group_cols = ["ID", "model", "set"] if aggregate else ["ID", "model", "set", "region"]
        drop_cols = ["region"] if aggregate else []
        metrics_df = metrics.drop(columns=drop_cols).groupby(group_cols).mean().reset_index()

        # Add 'region' column with value 'All' if it doesn't exist after aggregation
        if "region" not in metrics_df.columns:
            metrics_df["region"] = "ALL"

        # Merge aggregated metrics with features
        merged = metrics_df.merge(features, on=["ID", "set"])

        return merged

    def render_scatter_plot(self, data, x_axis, y_axis, aggregated):
        # Scatter plot visualization
        fig = multivariate_metric_feature(
            data=data,
            x_axis=x_axis,
            y_axis=self.metrics.get(y_axis),
            x_label=pretty_string(x_axis),
            y_label=y_axis,
            color="Dataset",
            facet_col="region" if not aggregated else None,
            highlighted_subjects=st.session_state.highlighted_subjects,
            template=self.template,
        )
        if not aggregated:
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        selected_points = plotly_events(fig, click_event=True, override_height=None)
        download_plot(fig, label="Single model performance", filename="single_model_performance")

        return selected_points

    def render_scatter_plot_with_customization(self, data, x_axis, y_axis, aggregated):
        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

        # Column 1: Display the plot
        with col1:
            scatter_metric = multivariate_metric_feature(
                data=data,
                x_axis=x_axis,
                y_axis=self.metrics.get(y_axis),
                x_label=pretty_string(x_axis),
                y_label=y_axis,
                color="Dataset",
                facet_col="region" if not aggregated else None,
                highlighted_subjects=st.session_state.highlighted_subjects,
                template=self.template,
            )
            if not aggregated:
                scatter_metric.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        with col2:
            update_plot_customization(scatter_metric, key="single_model")

        with col1:
            selected_points = plotly_events(scatter_metric, click_event=True, override_height=None)
            download_plot(scatter_metric, label="Univariate Analysis", filename="univariate_analysis")

        return selected_points

    @staticmethod
    def get_case_from_point(selected_points, data, aggregated):
        if selected_points and aggregated:
            point = selected_points[0]
            if point["curveNumber"] < len(data.set.unique()):
                point_subset = list(data.set.unique())[point["curveNumber"]]
                filtered_set_data = data[data.set == point_subset]
                selected_case = filtered_set_data.iloc[point["pointIndex"]]["ID"]

                # Add or remove the selected case
                try:
                    if selected_case not in st.session_state.highlighted_subjects:
                        st.session_state.dict_cases[(f"{point['x']}", f"{point['y']}")] = selected_case
                        st.session_state.highlighted_subjects.append(selected_case)
                except KeyError:
                    st.markdown(":red[Please, click on 'Reset highlighted cases' button below.]")

            else:
                selected_case = st.session_state.dict_cases[(f"{point['x']}", f"{point['y']}")]
                st.session_state.highlighted_subjects.remove(selected_case)
        if selected_points and not aggregated:
            st.markdown(
                ":red[Please, return to the aggregated view to highlight more cases and/or discard them or click on the "
                "'Reset highlighted cases' button below.]"
            )

    def scatter_plot_logic(self, data, x_axis, y_axis, aggregated, customization):
        # Initialize session state for highlighted subjects
        if "highlighted_subjects" not in st.session_state:
            st.session_state.highlighted_subjects = []
            st.session_state.dict_cases = {}

        if customization == "Standard visualization":
            selected_points = self.render_scatter_plot(data, x_axis, y_axis, aggregated)
        else:
            selected_points = self.render_scatter_plot_with_customization(data, x_axis, y_axis, aggregated)

        self.get_case_from_point(selected_points, data, aggregated)

        # Button to reset highlighted cases
        reset_selected_cases = st.button(label="Reset highlighted cases")
        if reset_selected_cases:
            self.reset_highlighted_cases()

    @staticmethod
    def reset_highlighted_cases():
        """
        Reset the highlighted cases.
        """
        st.session_state.highlighted_subjects = []
        st.session_state.dict_cases = {}
        st.rerun()
