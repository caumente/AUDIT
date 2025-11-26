import streamlit as st
from streamlit_plotly_events import plotly_events
from streamlit_theme import st_theme

from audit.app.util.commons.checks import health_checks
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import MultivariatePage
from audit.app.util.pages.base_page import BasePage
from audit.utils.external_tools.itk_snap import run_itk_snap
from audit.utils.internal._csv_helpers import read_datasets_from_dict
from audit.visualization.commons import update_plot_customization
from audit.visualization.scatter_plots import multivariate_features_highlighter


class MultivariateFeature(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = MultivariatePage()

    def run(self):
        theme = st_theme(key="univariate_theme")
        if theme is not None:
            self.template = theme.get("base")

        datasets_root_path = self.config.get("datasets_path")
        features_information = self.config.get("features")
        labels = self.config.get("labels")

        st.header(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        df = read_datasets_from_dict(features_information)

        selected_sets, selected_feature = self.setup_sidebar(df, features_information)
        proceed = health_checks(selected_sets, selected_feature)

        if proceed[0]:
            df = processing_data(df, sets=selected_sets)
            df.reset_index(drop=True, inplace=True)

            self.handle_selection(
                df, datasets_root_path, selected_feature[0], selected_feature[1], selected_feature[2], labels
            )
            st.markdown(self.descriptions.description)
        else:
            st.error(proceed[-1], icon="🚨")

    def setup_sidebar(self, data, data_paths):
        with st.sidebar:
            st.header("Configuration")
            selected_sets = self.sidebar.setup_sidebar_multi_datasets(data_paths)
            x_axis = self.sidebar.setup_sidebar_features(data, name="Features (X axis)", key="feat_x")
            y_axis = self.sidebar.setup_sidebar_features(data, name="Features (Y axis)", key="feat_y", f_index=1)
            color_axis = self.sidebar.setup_sidebar_color(data, name="Color feature", key="feat_col")

        return selected_sets, [x_axis, y_axis, color_axis]

    def scatter_plot_logic(self, data, x_axis, y_axis, color_axis, customization):
        if customization == "Standard visualization":
            selected_points, highlight_subject = self.render_scatter_plot(data, x_axis, y_axis, color_axis)
        else:
            selected_points, highlight_subject = self.render_scatter_plot_with_customization(
                data, x_axis, y_axis, color_axis
            )

        return selected_points, highlight_subject

    def render_scatter_plot(self, data, x_axis, y_axis, color_axis):
        highlight_subject = self.sidebar.setup_highlight_subject(data)

        fig = multivariate_features_highlighter(
            data=data,
            x_axis=x_axis,
            y_axis=y_axis,
            color=color_axis,
            x_label=self.features.get_pretty_feature_name(x_axis),
            y_label=self.features.get_pretty_feature_name(y_axis),
            legend_title=self.features.get_pretty_feature_name(color_axis) if color_axis != "Dataset" else None,
            highlight_point=highlight_subject,
            template=self.template,
        )

        selected_points = plotly_events(fig, click_event=True, override_height=None)
        download_plot(fig, label="Multivariate Analysis", filename="multivariate_analysis")

        return selected_points, highlight_subject

    def render_scatter_plot_with_customization(self, data, x_axis, y_axis, color_axis):
        highlight_subject = self.sidebar.setup_highlight_subject(data)

        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

        # Column 1: Display the plot
        with col1:
            scatter_fig = multivariate_features_highlighter(
                data=data,
                x_axis=x_axis,
                y_axis=y_axis,
                color=color_axis,
                x_label=self.features.get_pretty_feature_name(x_axis),
                y_label=self.features.get_pretty_feature_name(y_axis),
                legend_title=self.features.get_pretty_feature_name(color_axis) if color_axis != "Dataset" else None,
                highlight_point=highlight_subject,
                template=self.template,
            )
        # Column 2: Customization panel
        with col2:
            update_plot_customization(scatter_fig, key="scatter")

        with col1:
            selected_points = plotly_events(scatter_fig, click_event=True, override_height=None)
            download_plot(scatter_fig, label="Multivariate analysis", filename="multivariate_analysis")

        return selected_points, highlight_subject

    @staticmethod
    def get_case_from_point(data, selected_points, highlight_subject):
        selected_case = None
        if selected_points:
            try:
                point = selected_points[0]
                filtered_set_data = data[data.set == data.set.unique()[point["curveNumber"]]]
                selected_case = filtered_set_data.iloc[point["pointIndex"]]["ID"]
            except IndexError:
                selected_case = highlight_subject

        return selected_case

    @staticmethod
    def manage_itk_opening(data, datasets_root_path, labels, selected_points, selected_case):
        if "last_opened_case_itk" not in st.session_state:
            st.session_state.last_opened_case_itk = None
        if selected_case and selected_case != "Select a case" and len(selected_points) == 1:
            if selected_case != st.session_state.last_opened_case_itk:
                st.session_state.last_opened_case_itk = selected_case
                dataset = data[data.ID == selected_case]["set"].unique()[0]
                verification_check = run_itk_snap(
                    path=datasets_root_path, dataset=dataset, case=selected_case, labels=labels
                )
                if not verification_check:
                    st.error("Ups, something went wrong when opening the file in ITK-SNAP", icon="🚨")
                    st.session_state.last_opened_case_itk = None
                else:
                    st.write(f"Opened case {selected_case} in ITK-SNAP")

    def handle_selection(self, data, datasets_root_path, x_axis, y_axis, color_axis, labels):
        col1, col2 = st.columns([2, 2], gap="small")
        with col1:
            st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")
        with col2:
            customization_scatter = st.selectbox(
                label="Customize visualization",
                options=["Standard visualization", "Custom visualization"],
                index=0,
                key="scatter",
            )
        selected_points, highlight_subject = self.scatter_plot_logic(
            data, x_axis, y_axis, color_axis, customization_scatter
        )
        selected_case = self.get_case_from_point(data, selected_points, highlight_subject)
        self.manage_itk_opening(data, datasets_root_path, labels, selected_points, selected_case)
