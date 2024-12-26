import pandas as pd
import streamlit as st

from src.app.util.commons.data_preprocessing import processing_data
from src.app.util.commons.sidebars import setup_sidebar_longitudinal_subject
from src.app.util.commons.sidebars import setup_sidebar_single_dataset
from src.app.util.commons.sidebars import setup_sidebar_single_model
from src.app.util.commons.utils import download_plot
from src.app.util.constants.descriptions import LongitudinalAnalysisPage
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.file_manager import read_datasets_from_dict
from src.visualization.time_series import plot_longitudinal
from src.visualization.time_series import plot_longitudinal2

const = LongitudinalAnalysisPage()

# Load configuration and data
config = load_config_file("./src/configs/app.yml")
features_paths = config.get("features")
metrics_paths = config.get("metrics")


def setup_sidebar(data):

    with st.sidebar:
        st.header("Configuration")

        # Select datasets
        selected_set = setup_sidebar_single_dataset(data)
        selected_model = setup_sidebar_single_model(data)

        return selected_set, selected_model


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


def clean_longitudinal_id(value):
    value_str = str(value)

    if value_str.endswith('.0'):
        return value_str[:-2]

    return value_str


def plot_visualization(data):
    data = data.reset_index(drop=True)
    fig = plot_longitudinal(data)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True, scrolling=True)
    download_plot(fig, label="Relative Error in Lesion Size Estimation", filename="relative_error_in_LSE")

    # Description
    st.markdown(const.description)
    fig = plot_longitudinal2(data)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True, scrolling=True)
    download_plot(fig, label="Absolute Difference in Lesion Size Variation", filename="absolute_difference_in_LSV")


def longitudinal():
    # Define page layout
    st.header(const.header)
    st.markdown(const.sub_header)

    # Reading feature data
    features_df = read_datasets_from_dict(features_paths)
    metrics_df = read_datasets_from_dict(metrics_paths)
    merged = merge_features_metrics(features_df, metrics_df)

    if not merged.empty:
        # Sidebar setup
        selected_set, selected_model = setup_sidebar(merged)
        df = processing_data(
            data=merged,
            sets=selected_set,
            models=selected_model,
            features=["ID", "set", "longitudinal_id", "time_point", "lesion_size", "lesion_size_pred"]
        )

        # filter subject
        df['longitudinal_id'] = df['longitudinal_id'].apply(clean_longitudinal_id)
        selected_subject = setup_sidebar_longitudinal_subject(df)
        df = df[df.longitudinal_id == selected_subject]

        # Main functionality
        plot_visualization(df)
    else:
        st.error("Metric datasets must contain tumor size variable", icon="🚨")


