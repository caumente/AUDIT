import pandas as pd
import streamlit as st
from streamlit_plotly_events import plotly_events

from src.app.util.commons.checks import dataset_sanity_check
from src.app.util.commons.data_preprocessing import processing_data
from src.app.util.commons.sidebars import setup_aggregation_button
from src.app.util.commons.sidebars import setup_sidebar_features
from src.app.util.commons.sidebars import setup_sidebar_multi_datasets
from src.app.util.commons.sidebars import setup_sidebar_regions
from src.app.util.commons.sidebars import setup_sidebar_single_metric
from src.app.util.commons.sidebars import setup_sidebar_single_model
from src.app.util.constants.descriptions import ModelPerformanceAnalysisPage
from src.app.util.constants.metrics import Metrics
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.file_manager import read_datasets_from_dict
from src.utils.commons.strings import pretty_string
from src.visualization.scatter_plots import multivariate_metric_feature

# Load constants
const_descriptions = ModelPerformanceAnalysisPage()
const_metrics = Metrics()
metrics_dict = const_metrics.get_metrics()

# Load configuration file
config = load_config_file("./src/configs/app.yml")
metrics_paths = config.get("metrics")
features_paths = config.get("features")


def setup_sidebar(data, data_paths, aggregated):
    with st.sidebar:
        st.header("Configuration")

        selected_set = setup_sidebar_multi_datasets(data_paths)
        selected_model = setup_sidebar_single_model(data)
        selected_y_axis = setup_sidebar_single_metric(data)
        selected_x_axis = setup_sidebar_features(data, name="Feature")
        selected_regions = setup_sidebar_regions(data, aggregated)

    return selected_set, selected_model, selected_x_axis, selected_y_axis, selected_regions


def merge_features_and_metrics(features: pd.DataFrame, metrics: pd.DataFrame, aggregate=True) -> pd.DataFrame:
    # Aggregate metrics by ID, model, and set (optionally including region)
    group_cols = ["ID", "model", "set"] if aggregate else ["ID", "model", "set", "region"]
    metrics_df = metrics.groupby(group_cols).mean().reset_index()

    # Add 'region' column with value 'All' if it doesn't exist after aggregation
    if 'region' not in metrics_df.columns:
        metrics_df['region'] = 'ALL'

    # Merge aggregated metrics with features
    merged = metrics_df.merge(features, on=["ID", "set"])

    return merged


def visualize_data(data, x_axis, y_axis, aggregated):

    # Initialize session state for highlighted subjects
    if "highlighted_subjects" not in st.session_state:
        st.session_state.highlighted_subjects = []
        st.session_state.dict_cases = {}

    # Visualize scatter plot
    fig = multivariate_metric_feature(
        data=data,
        x_axis=x_axis,
        y_axis=metrics_dict.get(y_axis),
        x_label=pretty_string(x_axis),
        y_label=y_axis,
        color="Dataset",
        facet_col="region" if not aggregated else None,
        highlighted_subjects=st.session_state.highlighted_subjects,
    )
    if not aggregated:
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    selected_points = plotly_events(fig, click_event=True, override_height=None)

    process_selected_points(selected_points, data, aggregated)

    # Button to reset highlighted cases
    reset_selected_cases = st.button(label="Reset highlighted cases")
    if reset_selected_cases:
        reset_highlighted_cases()


def process_selected_points(selected_points, data, aggregated):
    if selected_points and aggregated:
        point = selected_points[0]
        if point["curveNumber"] < len(data.set.unique()):
            point_subset = list(data.set.unique())[point["curveNumber"]]
            filtered_set_data = data[data.set == point_subset]
            selected_case = filtered_set_data.iloc[point["pointIndex"]]["ID"]

            # Add or remove the selected case
            if selected_case not in st.session_state.highlighted_subjects:
                st.session_state.dict_cases[(f"{point['x']}", f"{point['y']}")] = selected_case
                st.session_state.highlighted_subjects.append(selected_case)
        else:
            selected_case = st.session_state.dict_cases[(f"{point['x']}", f"{point['y']}")]
            st.session_state.highlighted_subjects.remove(selected_case)
    if selected_points and not aggregated:
        st.markdown(
            ":red[Please, return to the aggregated view to highlight more cases and/or discard them or click on the "
            "'Reset highlighted cases' button below.]"
        )


def reset_highlighted_cases():
    """
    Reset the highlighted cases.
    """
    st.session_state.highlighted_subjects = []
    st.session_state.dict_cases = {}
    st.rerun()


def performance():
    # Define page
    st.subheader(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)

    # Load the data
    features_df = read_datasets_from_dict(features_paths)
    metrics_df = read_datasets_from_dict(metrics_paths)
    agg = setup_aggregation_button()
    st.markdown("**Double click on a point to highlight it in red and then visualize it disaggregated.**")
    merged_data = merge_features_and_metrics(features=features_df, metrics=metrics_df, aggregate=agg)

    # Setup sidebar
    selected_sets, selected_model, feature, metric, selected_regions = setup_sidebar(data=merged_data, data_paths=metrics_paths, aggregated=agg)
    if not dataset_sanity_check(selected_sets):
        st.error("Please, select a dataset from the left sidebar", icon="🚨")
    else:
        df = processing_data(merged_data, sets=selected_sets, models=selected_model, regions=selected_regions,
                             features=['ID', 'model', feature, metrics_dict.get(metric, None), 'set', 'region'])
        visualize_data(
            data=df,
            x_axis=feature,
            y_axis=metric,
            aggregated=agg,
        )

        st.markdown(const_descriptions.description)
