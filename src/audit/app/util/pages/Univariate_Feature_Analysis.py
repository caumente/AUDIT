import streamlit as st
from streamlit_plotly_events import plotly_events

from audit.app.util.commons.checks import health_checks
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.sidebars import setup_filtering_options
from audit.app.util.commons.sidebars import setup_highlight_subject
from audit.app.util.commons.sidebars import setup_histogram_options
from audit.app.util.commons.sidebars import setup_sidebar_features
from audit.app.util.commons.sidebars import setup_sidebar_multi_datasets
from audit.app.util.commons.sidebars import setup_sidebar_plot_customization
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import UnivariatePage
from audit.app.util.constants.features import Features
from audit.utils.commons.file_manager import read_datasets_from_dict
from audit.utils.external_tools.itk_snap import run_itk_snap
from audit.visualization.boxplot import boxplot_highlighter
from audit.visualization.histograms import custom_distplot
from audit.visualization.histograms import custom_histogram

# Load constants
const_descriptions = UnivariatePage()
const_features = Features()


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


def render_boxplot(data, feature, plot_type, highlight_subject):
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

    return selected_points


def render_boxplot_with_customization(data, feature, plot_type, highlight_subject):
    st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")

    # Create a layout with two columns: one for the plot and another for the customization panel
    col1, col2 = st.columns([4, 1], gap="small")  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

    # Column 1: Display the plot
    with col1:
        # Call the boxplot_highlighter function to generate the plot
        boxplot_fig = boxplot_highlighter(
            data,
            x_axis=feature,
            color_var="set",
            plot_type=plot_type,
            highlight_point=highlight_subject,
        )

    # Column 2: Customization panel
    with col2:
        show_leg, leg_pos, leg_x, leg_y, leg_xanc, leg_yanc, xlabel, ylabel, title = setup_sidebar_plot_customization()

        # Update the legend layout
        boxplot_fig.update_layout(
                legend=dict(
                    x=leg_x,
                    y=leg_y,
                    xanchor=leg_xanc,
                    yanchor=leg_yanc,
                )
        )

        boxplot_fig.update_layout(
            showlegend=show_leg,  # Show or hide the legend
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            title=dict(text=title, x=0.5),  # Center the title
        )

    # Render the adjusted plot in the main column
    with col1:
        selected_points = plotly_events(boxplot_fig, click_event=True, override_height=None)
        download_plot(boxplot_fig, label="Univariate Analysis", filename="univariate_analysis")

    return selected_points


def get_case_from_point(data, selected_points, highlight_subject):
    selected_case = None

    # last condition to avoid that clicking inside the boxplot randomly opens a subject
    if selected_points and len(selected_points) == 1:
        point = selected_points[0]
        filtered_set_data = data[data.set == point["y"]]
        if point["curveNumber"] < len(data.set.unique()):
            selected_case = filtered_set_data.iloc[point["pointIndex"]]["ID"]
        else:  # to open the case highlighted when clicking on it (because red points are new curves in the plot)
            selected_case = highlight_subject

    return selected_case


def manage_itk_opening(data, datasets_root_path, labels, selected_points, selected_case):
    # Visualize case in ITK-SNAP
    if "last_opened_case_itk" not in st.session_state:
        st.session_state.last_opened_case_itk = None
    # last condition to avoid that clicking inside the boxplot randomly opens a subject
    if selected_case and selected_case != "Select a case" and len(selected_points) == 1:
        if selected_case != st.session_state.last_opened_case_itk:
            st.session_state.last_opened_case_itk = selected_case
            dataset = data[data.ID == selected_case]["set"].unique()[0]
            verification_check = run_itk_snap(
                path=datasets_root_path,
                dataset=dataset,
                case=selected_case,
                labels=labels
            )
            if not verification_check:
                st.error("Ups, something went wrong when opening the file in ITK-SNAP", icon="🚨")
                st.session_state.last_opened_case_itk = None
            else:
                info_placeholder = st.empty()
                info_placeholder.write(f"Opened case {selected_case} in ITK-SNAP")


def boxplot_logic(datasets_root_path, data, feature, labels, plot_type, highlight_subject, customization=False):
    if customization == 'Standard visualization':
        selected_points = render_boxplot(data, feature, plot_type, highlight_subject)
    else:
        selected_points = render_boxplot_with_customization(data, feature, plot_type, highlight_subject)

    selected_case = get_case_from_point(data, selected_points, highlight_subject)

    manage_itk_opening(data, datasets_root_path, labels, selected_points, selected_case)


def main(data, datasets_paths, select_feature_name, labels):

    highlight_subject = setup_highlight_subject(data)

    # Visualize boxplot
    data.reset_index(drop=True, inplace=True)
    st.markdown(const_descriptions.description_boxplot)
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        plot_type = st.selectbox(label="Type of plot to visualize", options=["Box + Points", "Box", "Violin"], index=0)
    with col2:
        customization = st.selectbox(label="Customize visualization", options=["Standard visualization", "Custom visualization"], index=0)
    boxplot_logic(datasets_paths, data, select_feature_name, labels, plot_type, highlight_subject, customization)

    st.markdown("---")

    # Visualize histogram
    st.markdown(const_descriptions.description_distribution)
    plot_type = st.selectbox(label="Type of plot to visualize", options=["Histogram", "Probability"], index=1)
    n_bins, bins_size = setup_histogram_options(plot_type)
    histogram_logic(data, plot_type, select_feature_name, n_bins, bins_size)


def univariate(config):
    # Load configuration and data
    datasets_paths = config.get("datasets_path")
    features_paths = config.get("features")
    labels = config.get("labels")

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

        main(df, datasets_paths, selected_feature, labels)
    else:
        st.error(proceed[-1], icon='🚨')