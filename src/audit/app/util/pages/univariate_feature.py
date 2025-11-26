import numpy as np
import streamlit as st
from streamlit_plotly_events import plotly_events
from streamlit_theme import st_theme

from audit.app.util.commons.checks import health_checks
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import UnivariatePage
from audit.app.util.pages.base_page import BasePage
from audit.utils.external_tools.itk_snap import run_itk_snap
from audit.utils.internal._csv_helpers import read_datasets_from_dict
from audit.visualization.boxplot import boxplot_highlighter
from audit.visualization.commons import update_plot_customization
from audit.visualization.histograms import custom_distplot
from audit.visualization.histograms import custom_histogram


class UnivariateFeature(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = UnivariatePage()

    def run(self):
        theme = st_theme(key="univariate_theme")
        if theme is not None:
            self.template = theme.get("base")

        # Load configuration and data
        datasets_paths = self.config.get("datasets_path")
        features_paths = self.config.get("features")
        labels = self.config.get("labels")

        # Load configuration and data
        st.header(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        # Load datasets
        df = read_datasets_from_dict(features_paths)

        # Set up sidebar and plot options
        selected_sets, selected_feature = self.setup_sidebar(df, features_paths)
        filtering_method, r_low, r_up, c_low, c_up, num_std_devs = self.sidebar.setup_filtering_options(
            df, selected_feature
        )

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
                num_std_devs=num_std_devs,
            )
            try:
                self.main(df, datasets_paths, selected_feature, labels)
            except TypeError:
                st.error(
                    "Ups, something went wrong when searching for outliers. Please, make sure that all your metadata "
                    "columns are numeric, otherwise it is not possible to run the algorithm",
                    icon="🚨",
                )
        else:
            st.error(proceed[-1], icon="🚨")

    def setup_sidebar(self, data, data_paths):
        with st.sidebar:
            st.header("Configuration")

            selected_sets = self.sidebar.setup_sidebar_multi_datasets(data_paths)
            select_feature = self.sidebar.setup_sidebar_features(data, name="Features", key="features")

        return selected_sets, select_feature

    def boxplot_logic(
        self,
        datasets_root_path,
        data,
        feature,
        labels,
        plot_type,
        highlight_subject,
        customization="Standard visualization",
    ):
        if customization == "Standard visualization":
            selected_points = self.render_boxplot(data, feature, plot_type, highlight_subject)
        else:
            selected_points = self.render_boxplot_with_customization(data, feature, plot_type, highlight_subject)

        selected_case = self.get_case_from_point(data, selected_points, highlight_subject)

        self.manage_itk_opening(data, datasets_root_path, labels, selected_points, selected_case)

    def render_boxplot(self, data, feature, plot_type, highlight_subject):
        st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")

        boxplot_fig = boxplot_highlighter(
            data,
            x_axis=feature,
            color_var="set",
            plot_type=plot_type,
            highlight_point=highlight_subject,
            template=self.template,
        )
        selected_points = plotly_events(boxplot_fig, click_event=True, override_height=None)
        download_plot(boxplot_fig, label="Univariate Analysis", filename="univariate_analysis")

        return selected_points

    def render_boxplot_with_customization(self, data, feature, plot_type, highlight_subject):
        st.markdown("**Click on a point to visualize it in ITK-SNAP app.**")

        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

        # Column 1: Display the plot
        with col1:
            # Call the boxplot_highlighter function to generate the plot
            boxplot_fig = boxplot_highlighter(
                data,
                x_axis=feature,
                color_var="set",
                plot_type=plot_type,
                highlight_point=highlight_subject,
                template=self.template,
            )

        # Column 2: Customization panel
        with col2:
            update_plot_customization(boxplot_fig, key="boxplot")

        # Render the adjusted plot in the main column
        with col1:
            selected_points = plotly_events(boxplot_fig, click_event=True, override_height=None)
            download_plot(boxplot_fig, label="Univariate Analysis", filename="univariate_analysis")

        return selected_points

    def render_probability_distribution(self, data, feature):
        try:
            fig = custom_distplot(data, x_axis=feature, color_var="set", histnorm="probability", template=self.template)
        except np.linalg.LinAlgError as e:
            st.write(":red[Error generating the histogram: KDE failed due to singular covariance matrix.]")
            st.write(":red[This may happen when the data has low variance or is nearly constant.]")
            st.write(":red[Consider removing filters or datasets]")
            fig = None
        except Exception as e:
            st.write(":red[An unexpected error occurred while generating the histogram.]")
            st.write(f"Details: {str(e)}")
            fig = None

        if fig is not None:
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            download_plot(fig, label="Data Distribution", filename="distribution")
            st.markdown(self.descriptions.description)

    def render_probability_distribution_with_customization(self, data, feature):
        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

        # Column 1: Display the plot
        with col1:
            try:
                distplot_fig = custom_distplot(
                    data, x_axis=feature, color_var="set", histnorm="probability", template=self.template
                )
            except np.linalg.LinAlgError as e:
                st.write(":red[Error generating the histogram: KDE failed due to singular covariance matrix.]")
                st.write(":red[This may happen when the data has low variance or is nearly constant.]")
                st.write(":red[Consider removing filters or datasets]")
                distplot_fig = None
            except Exception as e:
                st.write(":red[An unexpected error occurred while generating the histogram.]")
                st.write(f"Details: {str(e)}")
                distplot_fig = None

        # Column 2: Customization panel
        with col2:
            update_plot_customization(distplot_fig, key="distplot")

        # Render the adjusted plot in the main column
        with col1:
            if distplot_fig is not None:
                st.plotly_chart(distplot_fig, theme="streamlit", use_container_width=True)
                download_plot(distplot_fig, label="Data Distribution", filename="distribution")
                st.markdown(self.descriptions.description)

    def render_histogram(self, data, feature, n_bins, bins_size):
        fig = None
        if n_bins:
            fig = custom_histogram(data, x_axis=feature, color_var="set", n_bins=n_bins, template=self.template)
        elif bins_size:
            fig = custom_histogram(
                data, x_axis=feature, color_var="set", n_bins=None, bins_size=bins_size, template=self.template
            )
        else:
            st.write(":red[Please, select the number of bins or bins size]")

        if fig is not None:
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            download_plot(fig, label="Data Distribution", filename="distribution")
            st.markdown(self.descriptions.description)

    def render_histogram_with_customization(self, data, feature, n_bins, bins_size):
        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel

        # Column 1: Display the plot
        with col1:
            histogram = None
            if n_bins:
                histogram_fig = custom_histogram(
                    data, x_axis=feature, color_var="set", n_bins=n_bins, template=self.template
                )
            elif bins_size:
                histogram_fig = custom_histogram(
                    data, x_axis=feature, color_var="set", n_bins=None, bins_size=bins_size, template=self.template
                )
            else:
                st.write(":red[Please, select the number of bins or bins size]")

        # Column 2: Customization panel
        with col2:
            update_plot_customization(histogram_fig, key="histogram")

        # Render the adjusted plot in the main column
        with col1:
            if histogram_fig is not None:
                st.plotly_chart(histogram_fig, theme="streamlit", use_container_width=True)
                download_plot(histogram_fig, label="Data Distribution", filename="distribution")
                st.markdown(self.descriptions.description)

    def histogram_logic(self, data, plot_type, feature, n_bins, bins_size, customization="Standard visualization"):
        if customization == "Standard visualization":
            if plot_type == "Probability":
                self.render_probability_distribution(data, feature)
            else:
                self.render_histogram(data, feature, n_bins, bins_size)
        else:
            if plot_type == "Probability":
                self.render_probability_distribution_with_customization(data, feature)
            else:
                self.render_histogram_with_customization(data, feature, n_bins, bins_size)

    @staticmethod
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

    @staticmethod
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
                    path=datasets_root_path, dataset=dataset, case=selected_case, labels=labels
                )
                if not verification_check:
                    st.error("Ups, something went wrong when opening the file in ITK-SNAP", icon="🚨")
                    st.session_state.last_opened_case_itk = None
                else:
                    info_placeholder = st.empty()
                    info_placeholder.write(f"Opened case {selected_case} in ITK-SNAP")

    def main(self, data, datasets_paths, select_feature_name, labels):
        highlight_subject = self.sidebar.setup_highlight_subject(data)

        # Visualize boxplot
        data.reset_index(drop=True, inplace=True)
        st.markdown(self.descriptions.description_boxplot)
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            plot_type = st.selectbox(
                label="Type of plot to visualize", options=["Box + Points", "Box", "Violin"], index=0
            )
        with col2:
            customization_boxplot = st.selectbox(
                label="Customize visualization",
                options=["Standard visualization", "Custom visualization"],
                index=0,
                key="boxplot",
            )
        self.boxplot_logic(
            datasets_paths, data, select_feature_name, labels, plot_type, highlight_subject, customization_boxplot
        )

        st.markdown("---")

        # Visualize histogram
        st.markdown(self.descriptions.description_distribution)
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            plot_type = st.selectbox(label="Type of plot to visualize", options=["Histogram", "Probability"], index=1)
        with col2:
            customization_histogram = st.selectbox(
                label="Customize visualization",
                options=["Standard visualization", "Custom visualization"],
                index=0,
                key="histogram",
            )
        n_bins, bins_size = self.sidebar.setup_histogram_options(plot_type)
        self.histogram_logic(data, plot_type, select_feature_name, n_bins, bins_size, customization_histogram)
