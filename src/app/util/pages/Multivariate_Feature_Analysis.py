import streamlit as st
from streamlit_plotly_events import plotly_events

from src.app.util.commons.checks import health_checks
from src.app.util.commons.data_preprocessing import processing_data
from src.app.util.commons.sidebars import setup_highlight_subject
from src.app.util.commons.sidebars import setup_sidebar_color
from src.app.util.commons.sidebars import setup_sidebar_features
from src.app.util.commons.sidebars import setup_sidebar_multi_datasets
from src.app.util.commons.utils import download_plot
from src.app.util.constants.descriptions import MultivariatePage
from src.app.util.constants.features import Features
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.file_manager import read_datasets_from_dict
from src.utils.external_tools.itk_snap import run_itk_snap
from src.visualization.scatter_plots import multivariate_features_highlighter

# Load constants
const_descriptions = MultivariatePage()
const_features = Features()

# Load configuration
config = load_config_file("./src/configs/app.yml")
datasets_root_path = config.get("datasets_path")
features_information = config.get("features")


def setup_sidebar(data, data_paths):
    with st.sidebar:
        st.header("Configuration")

        selected_sets = setup_sidebar_multi_datasets(data_paths)
        select_x_axis = setup_sidebar_features(data, name="Features (X axis)", key="feat_x")
        select_y_axis = setup_sidebar_features(data, name="Features (Y axis)", key="feat_y", f_index=1)
        select_color_axis = setup_sidebar_color(data, name="Color feature", key="feat_col")

        return selected_sets, select_x_axis, select_y_axis, select_color_axis


def main(data, x_axis, y_axis, color_axis):
    # Scatter plot visualization
    st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")

    highlight_subject = setup_highlight_subject(data)

    fig = multivariate_features_highlighter(
        data=data,
        x_axis=x_axis,
        y_axis=y_axis,
        color=color_axis,
        highlight_point=highlight_subject,
    )
    selected_points = plotly_events(fig, click_event=True, override_height=None)
    download_plot(fig, label="Multivariate Analysis", filename="multivariate_analysis")

    # retrieving selected ID
    selected_case, st.session_state.selected_case = None, None
    if selected_points:
        try:
            point = selected_points[0]
            filtered_set_data = data[data.set == data.set.unique()[point["curveNumber"]]]
            selected_case = filtered_set_data.iloc[point["pointIndex"]]["ID"]
        except IndexError:
            selected_case = highlight_subject

    # Visualize case in ITK-SNAP
    if selected_case != st.session_state.selected_case:
        st.session_state.selected_case = selected_case
        dataset = data[data.ID == selected_case]["set"].unique()[0].lower()
        verification_check = run_itk_snap(datasets_root_path, dataset, selected_case, config.get("labels"))
        if not verification_check:
            st.error("Ups, something went wrong when opening the file in ITK-SNAP", icon="🚨")


def multivariate():
    # Define page layout
    st.header(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)

    # Load datasets
    df = read_datasets_from_dict(features_information)

    # Sidebar setup
    selected_sets, select_x_feature_name, select_y_feature_name, select_color_feature_name = setup_sidebar(df, features_information)

    proceed = health_checks(selected_sets, [select_x_feature_name, select_y_feature_name, select_color_feature_name])
    if proceed[0]:

        df = processing_data(df, sets=selected_sets)
        df.reset_index(drop=True, inplace=True)

        main(df, select_x_feature_name, select_y_feature_name, select_color_feature_name)

        st.markdown(const_descriptions.description)
    else:
        st.error(proceed[-1], icon='🚨')


