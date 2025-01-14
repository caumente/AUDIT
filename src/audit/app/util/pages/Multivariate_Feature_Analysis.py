import os
import streamlit as st
from streamlit_plotly_events import plotly_events

from audit.app.util.pages.BasePage import BasePage
from audit.app.util.commons.checks import health_checks
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.sidebars import setup_highlight_subject
from audit.app.util.commons.sidebars import setup_sidebar_color
from audit.app.util.commons.sidebars import setup_sidebar_features
from audit.app.util.commons.sidebars import setup_sidebar_multi_datasets
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import MultivariatePage
from audit.utils.commons.file_manager import read_datasets_from_dict
from audit.utils.external_tools.itk_snap import run_itk_snap
from audit.visualization.scatter_plots import multivariate_features_highlighter


class MultivariateFeatureAnalysis(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = MultivariatePage()

    def run(self):
        datasets_root_path = self.config.get("datasets_path")
        features_information = self.config.get("features")
        labels = self.config.get("labels")

        st.header(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        df = read_datasets_from_dict(features_information)

        sidebar_info = self.setup_sidebar(df, features_information)
        proceed = health_checks(sidebar_info.values())
        if proceed[0]:
            df = processing_data(df, sets=sidebar_info["selected_sets"])
            df.reset_index(drop=True, inplace=True)

            self.handle_selection(
                df, datasets_root_path,
                sidebar_info["x_axis"], sidebar_info["y_axis"],
                sidebar_info["color_axis"], labels
            )

            st.markdown(self.descriptions.description)
        else:
            st.error(proceed[-1], icon='🚨')

    @staticmethod
    def setup_sidebar(data, data_paths):
        with st.sidebar:
            st.header("Configuration")
            return {
                "selected_sets": setup_sidebar_multi_datasets(data_paths),
                "x_axis": setup_sidebar_features(data, name="Features (X axis)", key="feat_x"),
                "y_axis": setup_sidebar_features(data, name="Features (Y axis)", key="feat_y", f_index=1),
                "color_axis": setup_sidebar_color(data, name="Color feature", key="feat_col"),
            }

    def render_scatter_plot(self, data, x_axis, y_axis, color_axis):
        st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")
        highlight_subject = setup_highlight_subject(data)

        fig = multivariate_features_highlighter(
            data=data,
            x_axis=x_axis,
            y_axis=y_axis,
            color=color_axis,
            x_label=self.features.get_pretty_feature_name(x_axis),
            y_label=self.features.get_pretty_feature_name(y_axis),
            legend_title=self.features.get_pretty_feature_name(y_axis) if color_axis != "Dataset" else None,
            highlight_point=highlight_subject,
        )

        selected_points = plotly_events(fig, click_event=True, override_height=None)
        download_plot(fig, label="Multivariate Analysis", filename="multivariate_analysis")

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
                    path=datasets_root_path,
                    dataset=dataset,
                    case=selected_case,
                    labels=labels
                )
                if not verification_check:
                    st.error("Ups, something went wrong when opening the file in ITK-SNAP", icon="🚨")
                    st.session_state.last_opened_case_itk = None
                else:
                    st.write(f"Opened case {selected_case} in ITK-SNAP")

    def handle_selection(self, data, datasets_root_path, x_axis, y_axis, color_axis, labels):
        selected_points, highlight_subject = self.render_scatter_plot(data, x_axis, y_axis, color_axis)
        selected_case = self.get_case_from_point(data, selected_points, highlight_subject)
        self.manage_itk_opening(data, datasets_root_path, labels, selected_points, selected_case)
