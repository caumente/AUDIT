import pandas as pd
import streamlit as st
from streamlit_theme import st_theme

from audit.app.util.commons.checks import none_check
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import MultiModelPerformanceComparisonsPage
from audit.app.util.constants.metrics import Metrics
from audit.app.util.pages.base_page import BasePage
from audit.utils.internal._csv_helpers import read_datasets_from_dict
from audit.visualization.boxplot import models_performance_boxplot
from audit.visualization.commons import update_multimodel_plot


class MultiModelPerformance(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = MultiModelPerformanceComparisonsPage()
        self.metrics = Metrics().get_metrics()

    def run(self):
        theme = st_theme(key="multimodel_theme")
        if theme is not None:
            self.template = theme.get("base")

        # load config files
        metrics_paths = self.config.get("metrics")
        labels_dict = self.config.get("labels")

        # Defining page
        st.subheader(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        proceed = none_check(metrics_paths=metrics_paths, labels_dict=labels_dict)
        if proceed[0]:
            # Load the data
            raw_metrics = read_datasets_from_dict(metrics_paths)
            agg = self.sidebar.setup_aggregation_button()

            # calling main function
            selected_set, selected_models, selected_regions, selected_metrics = self.setup_sidebar(raw_metrics)

            df = processing_data(
                data=raw_metrics,
                models=selected_models,
                sets=selected_set,
                regions=selected_regions,
                features=["ID", "region", "model", "set"] + selected_metrics,
            )

            data_melted = self.main_table(df, agg)

            # Create a layout with two columns: one for the plot and another for the customization panel
            col1, col2 = st.columns([1, 1], gap="small")
            with col1:
                st.markdown(self.descriptions.description)
            with col2:
                customization_boxplot = st.selectbox(
                    label="Customize visualization",
                    options=["Standard visualization", "Custom visualization"],
                    index=0,
                    key="multimodel",
                )

            if customization_boxplot == "Standard visualization":
                self.visualize_data(data_melted, agg)
            else:
                self.visualize_data_with_customization(data_melted, labels_dict, agg)
        else:
            st.error(proceed[-1], icon="🚨")

    def setup_sidebar(self, data):
        with st.sidebar:
            st.header("Configuration")

            selected_set = self.sidebar.setup_sidebar_single_dataset(data)
            selected_models = self.sidebar.setup_sidebar_multi_model(data)
            selected_regions = self.sidebar.setup_sidebar_regions(data, aggregated=False)
            selected_metrics = self.sidebar.setup_sidebar_multi_metrics(data)
            selected_metrics = [self.metrics.get(m) for m in selected_metrics]

        return selected_set, selected_models, selected_regions, selected_metrics

    def visualize_data(self, data, agg):
        fig = models_performance_boxplot(data, aggregated=agg, template=self.template)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        download_plot(fig, label="Models performance", filename="multimodel_performance")

    def visualize_data_with_customization(self, data, labels_dict, agg):
        # Create a layout with two columns: one for the plot and another for the customization panel
        col1, col2 = st.columns(
            [4, 1], gap="small"
        )  # Column 1 is larger for the plot, column 2 is smaller for the customization panel
        with col1:
            fig = models_performance_boxplot(data, aggregated=agg, template=self.template)
        with col2:
            update_multimodel_plot(fig, classes=labels_dict if not agg else {}, key="multimodel")

        with col1:
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            download_plot(fig, label="Models performance", filename="multimodel_performance")

    def main_table(self, data, aggregate):
        # postprocessing data
        data.rename(columns={v: k for k, v in self.metrics.items()}, inplace=True)
        data_melted = pd.melt(
            data,
            id_vars=["model", "region"],
            var_name="metric",
            value_name="score",
            value_vars=data.drop(columns=["ID", "model", "region", "set"]).columns,
        )

        # general results
        group_cols = ["model", "region"] if not aggregate else ["model"]
        drop_cols = ["region"] if aggregate else []
        aggregated = data.drop(columns=["ID", "set"] + drop_cols).groupby(group_cols).agg(["mean", "std"])

        # formatting results
        formatted = pd.DataFrame(index=aggregated.index)
        for metric in data_melted.metric.unique():
            formatted[metric] = aggregated[metric].apply(lambda x: f"{x['mean']:.3f} ± {x['std']:.3f}", axis=1)
        st.dataframe(formatted, use_container_width=True)

        return data_melted
