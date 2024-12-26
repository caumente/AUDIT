import streamlit as st
from streamlit_plotly_events import plotly_events

from src.app.util.commons.checks import health_checks
from src.app.util.commons.data_preprocessing import processing_data
from src.app.util.commons.sidebars import setup_filtering_options
from src.app.util.commons.sidebars import setup_highlight_subject
from src.app.util.commons.sidebars import setup_histogram_options
from src.app.util.commons.sidebars import setup_sidebar_features
from src.app.util.commons.sidebars import setup_sidebar_multi_datasets
from src.app.util.commons.utils import download_plot
from src.app.util.constants.descriptions import UnivariatePage
from src.app.util.constants.features import Features
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.file_manager import read_datasets_from_dict
from src.utils.external_tools.itk_snap import run_itk_snap
from src.visualization.boxplot import boxplot_highlighter
from src.visualization.histograms import custom_distplot
from src.visualization.histograms import custom_histogram

# Load constants
const_descriptions = UnivariatePage()
const_features = Features()

# Load configuration and data
config = load_config_file("./src/configs/app.yml")
datasets_paths = config.get("datasets_path")
features_paths = config.get("features")


def setup_sidebar(data, data_paths):
    with st.sidebar:
        st.header("Configuration")

        selected_sets = setup_sidebar_multi_datasets(data_paths)
        select_feature = setup_sidebar_features(data, name="Features", key="features")

    return selected_sets, select_feature


def histogram_logic(data, plot_type, feature, n_bins, bins_size):
    if plot_type == "Probability":
        fig = custom_distplot(data, x_axis=feature, color_var="set", histnorm="probability")
    else:
        if n_bins:
            fig = custom_histogram(data, x_axis=feature, color_var="set", n_bins=n_bins)
        elif bins_size:
            fig = custom_histogram(data, x_axis=feature, color_var="set", n_bins=None, bins_size=bins_size)
        else:
            st.write(":red[Please, select the number of bins or bins size]",)

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    download_plot(fig, label="Data Distribution", filename="distribution")
    st.markdown(const_descriptions.description)


def boxplot_logic(datasets_root_path, data, feature, labels, plot_type, highlight_subject):
    st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")

    boxplot_fig = boxplot_highlighter(
        data,
        x_axis=feature,
        color_var="set",
        plot_type=plot_type,
        highlight_point=highlight_subject,
    )
    selected_points = plotly_events(boxplot_fig, click_event=True, override_height=None)
    download_plot(boxplot_fig, label="Univariate Analysis", filename="univariate_analysis")

    selected_case, st.session_state.selected_case = None, None

    # Handle selected point
    info_placeholder = st.empty()
    # last condition to avoid that clicking inside the boxplot randomly opens a subject
    if selected_points and len(selected_points) == 1:
        point = selected_points[0]
        filtered_set_data = data[data.set == point["y"]]
        if point["curveNumber"] < len(data.set.unique()):
            selected_case = filtered_set_data.iloc[point["pointIndex"]]["ID"]
        else:  # to open the case highlighted when clicking on it
            selected_case = highlight_subject
        info_placeholder.write(f"Open ITK-SNAP for visualizing the case: {selected_case}")

    # Visualize case in ITK-SNAP
    if selected_case != st.session_state.selected_case:
        st.session_state.selected_case = selected_case
        # last condition to avoid that clicking inside the boxplot randomly opens a subject
        if selected_case and selected_case != "Select a case" and len(selected_points) == 1:
            dataset = data[data.ID == selected_case]["set"].unique()[0]
            verification_check = run_itk_snap(
                path=datasets_root_path,
                dataset=dataset,
                case=selected_case,
                labels=labels
            )
            if not verification_check:
                st.error("Ups, something wrong happened when opening the file in ITK-SNAP", icon="🚨")


def main(data, select_feature_name):

    highlight_subject = setup_highlight_subject(data)

    # Visualize boxplot
    st.subheader("Boxplot")
    data.reset_index(drop=True, inplace=True)
    st.markdown(const_descriptions.description_boxplot)
    plot_type = st.selectbox(label="Type of plot to visualize", options=["Box + Points", "Box", "Violin"], index=0)
    boxplot_logic(datasets_paths, data, select_feature_name, config.get("labels"), plot_type, highlight_subject)

    # Visualize histogram
    st.subheader("Continuous distribution")
    st.markdown(const_descriptions.description_distribution)
    plot_type = st.selectbox(label="Type of plot to visualize", options=["Histogram", "Probability"], index=1)
    n_bins, bins_size = setup_histogram_options(plot_type)
    histogram_logic(data, plot_type, select_feature_name, n_bins, bins_size)


def univariate():
    # Load configuration and data
    st.header(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)

    # Load datasets
    df = read_datasets_from_dict(features_paths)

    # Set up sidebar and plot options
    selected_sets, selected_feature = setup_sidebar(df, features_paths)
    filtering_method, r_low, r_up, c_low, c_up, num_std_devs = setup_filtering_options(df, selected_feature)

    proceed = health_checks(selected_sets, [selected_feature])
    if proceed[0]:

        # filtering data
        df = processing_data(
            data=df,
            sets=selected_sets,
            filtering_method=filtering_method,
            filtering_feature=selected_feature,
            remove_low=r_low,
            remove_up=r_up,
            clip_low=c_low,
            clip_up=c_up,
            num_std_devs=num_std_devs
        )

        main(df, selected_feature)
    else:
        st.error(proceed[-1], icon='🚨')