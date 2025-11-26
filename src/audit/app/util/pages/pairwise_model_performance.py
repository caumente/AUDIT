import numpy as np
import pandas as pd
import streamlit as st
from streamlit_theme import st_theme

from audit.app.util.commons.checks import models_sanity_check
from audit.app.util.commons.checks import none_check
from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import PairwiseModelPerformanceComparisonPage
from audit.app.util.constants.metrics import Metrics
from audit.app.util.pages.base_page import BasePage
from audit.metrics.commons import calculate_improvements
from audit.metrics.statistical_tests import homoscedasticity_test
from audit.metrics.statistical_tests import normality_test
from audit.metrics.statistical_tests import paired_ttest
from audit.metrics.statistical_tests import wilcoxon_test
from audit.utils.internal._csv_helpers import read_datasets_from_dict
from audit.visualization.barplots import aggregated_pairwise_model_performance
from audit.visualization.barplots import individual_pairwise_model_performance
from audit.visualization.histograms import plot_histogram


class PairwiseModelPerformance(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = PairwiseModelPerformanceComparisonPage()
        self.metrics = Metrics()

    def run(self):
        theme = st_theme(key="pairwise_theme")
        if theme is not None:
            self.template = theme.get("base")

        # Load configuration files
        metrics_paths = self.config.get("metrics")
        features_paths = self.config.get("features")

        # Defining page
        st.subheader(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)
        show_descriptions = st.toggle("Show formulas")
        if show_descriptions:
            st.markdown(self.descriptions.description)
            st.latex(self.descriptions.absolute_formula)
            st.latex(self.descriptions.relative_formula)
            st.latex(self.descriptions.ratio_formula)

        # type of improvement and aggregation
        improvement_type = self.sidebar.setup_improvement_button()
        agg = self.sidebar.setup_aggregation_button()

        proceed = none_check(metrics_paths=metrics_paths, features_paths=features_paths)
        if proceed[0]:
            # Load datasets
            raw_metrics = read_datasets_from_dict(metrics_paths)
            raw_features = read_datasets_from_dict(features_paths)
            df_stats = raw_metrics.drop(columns="region").groupby(["ID", "model", "set"]).mean().reset_index()

            # Setup sidebar
            (
                selected_set,
                ba_model,
                be_model,
                selected_metric,
                num_subjects,
                selected_sorted,
                selected_order,
            ) = self.setup_sidebar(raw_metrics, agg)

            if not models_sanity_check(ba_model, be_model):
                st.error("Models selected must be different to make a performance comparison", icon="🚨")
            else:
                df = processing_data(
                    raw_metrics,
                    selected_set,
                    features=["ID", "region", self.metrics.get_metrics().get(selected_metric, None), "model", "set"],
                )
                df = self.process_metrics(
                    data=df.drop(columns="set"),
                    selected_metric=self.metrics.get_metrics().get(selected_metric, None),
                    baseline_model=ba_model,
                    benchmark_model=be_model,
                    aggregate=agg,
                    improvement_type=improvement_type,
                )

                # Merge with features and average performance if not aggregated
                if not agg:
                    df = df.merge(raw_features, on=["ID"])
                    self.run_individualized(
                        df, ba_model, be_model, improvement_type, selected_sorted, selected_order, num_subjects
                    )
                else:
                    self.run_aggregated(df, improvement_type, selected_metric, selected_set)

                    # Perform statistical test
                    if self.sidebar.setup_statistical_test():
                        (
                            sample_bm,
                            sample_nm,
                            nt_baseline_model,
                            nt_benchmark_model,
                            homoscedasticity,
                        ) = self.perform_parametric_assumptions_test(
                            df_stats, selected_set, selected_metric, ba_model, be_model
                        )
                        self.perform_statistical_test(
                            nt_baseline_model, nt_benchmark_model, homoscedasticity, sample_bm, sample_nm
                        )

                        self.sidebar.setup_button_data_download(df_stats)
        else:
            st.error(proceed[-1], icon="🚨")

    def setup_sidebar(self, data, aggregated=True):
        with st.sidebar:
            st.header("Configuration")

            selected_set = self.sidebar.setup_sidebar_single_dataset(data)
            baseline_model, benchmark_model = self.sidebar.setup_sidebar_pairwise_models(data, selected_set)
            selected_metric = self.sidebar.setup_sidebar_single_metric(data)
            num_max_subjects, selected_sorted, selected_order = self.sidebar.setup_metrics_customization(
                baseline_model, benchmark_model, aggregated
            )

        return (
            selected_set,
            baseline_model,
            benchmark_model,
            selected_metric,
            num_max_subjects,
            selected_sorted,
            selected_order,
        )

    def process_metrics(
        self, data, selected_metric, baseline_model, benchmark_model, aggregate=False, improvement_type="Absolute"
    ):
        index_cols = ["ID", "region"]

        if aggregate:
            data = data.drop(columns=["ID"]).groupby(["region", "model"]).mean().reset_index()
            index_cols.remove("ID")

        # pivot table
        pivot_df = data[index_cols + ["model", selected_metric]]
        pivot_df = pivot_df.pivot_table(index=index_cols, columns="model", values=selected_metric).reset_index()

        # add averages
        if aggregate:
            averages = pd.DataFrame([pivot_df.mean(numeric_only=True, skipna=True)])
            averages["region"] = "Average"
        else:
            averages = pivot_df.groupby("ID").mean(numeric_only=True).reset_index()
            averages["region"] = "Average"
        pivot_df = pd.concat([pivot_df, averages], ignore_index=True)

        # computing improvements
        out = calculate_improvements(pivot_df, baseline_model, benchmark_model)
        out["metric"] = selected_metric
        out["color_bar"] = np.where(
            out[improvement_type] < 0,
            self.descriptions.colorbar.get("decrease"),
            self.descriptions.colorbar.get("increase"),
        )

        return out

    def run_individualized(
        self, data, baseline_model, benchmark_model, improvement_type, selected_sorted, selected_order, num_max_subjects
    ):
        # Sort dataset
        l = data[data.region == "Average"].sort_values(by=selected_sorted, ascending=selected_order)["ID"]
        data["ID"] = pd.Categorical(data["ID"], categories=l, ordered=True)
        data = data.sort_values(["ID", "region"])

        # Filter based on the number of subjects
        if num_max_subjects:
            data = data[data.ID.isin(l[:num_max_subjects])]

        # Clip metric
        clip_low, clip_up = self.sidebar.setup_clip_sidebar(data, improvement_type)
        if clip_low is not None and clip_up is not None:
            data[improvement_type] = data[improvement_type].clip(clip_low, clip_up)

        all_figures = individual_pairwise_model_performance(
            data, baseline_model, benchmark_model, improvement_type, self.template
        )
        for fig in all_figures:
            st.plotly_chart(fig, theme="streamlit", use_container_width=False, scrolling=True)

    def run_aggregated(self, data, improvement_type, selected_metric, selected_set):
        fig = aggregated_pairwise_model_performance(
            data, improvement_type, selected_metric, selected_set, self.template
        )
        st.plotly_chart(fig, theme="streamlit", use_container_width=False, scrolling=True)
        download_plot(fig, label="Aggregated Pairwise Model Performance", filename="agg_pairwise_model_performance")

    @staticmethod
    def visualize_histogram(data, model):
        fig = plot_histogram(
            data=data[[model]],
            x_axis=model,
            color_var=None,
            n_bins=10,
            x_label=model,
        )

        return fig

    def perform_parametric_assumptions_test(self, data, selected_set, selected_metric, baseline_model, benchmark_model):
        st.markdown("""**Performing normality test:**""")
        col1, col2 = st.columns(2)
        df_wide = data[data.set == selected_set][["ID", "model", self.metrics.get_metrics().get(selected_metric, None)]]
        df_wide = df_wide.pivot(
            index="ID", columns="model", values=self.metrics.get_metrics().get(selected_metric, None)
        )

        sample_baseline_model = df_wide[baseline_model]
        sample_benchmark_model = df_wide[benchmark_model]

        with col1:
            # checking normality baseline model
            normality_test_bas_model = normality_test(sample_baseline_model)
            st.table(
                pd.DataFrame(normality_test_bas_model.items(), columns=["Metric", "Baseline model"]).set_index("Metric")
            )
            st.plotly_chart(
                self.visualize_histogram(df_wide, baseline_model),
                theme="streamlit",
                use_container_width=True,
                scrolling=True,
            )

        with col2:
            # checking normality benchmark model
            normality_test_ben_model = normality_test(sample_benchmark_model)
            st.table(
                pd.DataFrame(normality_test_ben_model.items(), columns=["Metric", "Benchmark model"]).set_index(
                    "Metric"
                )
            )
            st.plotly_chart(
                self.visualize_histogram(df_wide, benchmark_model),
                theme="streamlit",
                use_container_width=True,
                scrolling=True,
            )

        homoscedasticity = homoscedasticity_test(sample_baseline_model, sample_benchmark_model)

        return (
            sample_baseline_model,
            sample_benchmark_model,
            normality_test_bas_model,
            normality_test_ben_model,
            homoscedasticity,
        )

    @staticmethod
    def perform_statistical_test(
        normality_test_baseline_model,
        normality_test_benchmark_model,
        homoscedasticity,
        sample_baseline_model,
        sample_benchmark_model,
    ):
        st.markdown("""**Performing statistical test:**""")

        normal_baseline = normality_test_baseline_model["Normally distributed"]
        normal_benchmark = normality_test_benchmark_model["Normally distributed"]
        homoscedastic = homoscedasticity["Homoscedastic"]

        if normal_baseline and normal_benchmark and homoscedastic:
            st.markdown(
                """
            Both the baseline and benchmark samples are normally distributed and have equal variances.
            Therefore, the **Paired Student's t-test** will be performed. This parametric test compares two
            **paired samples** under the assumptions of normality and homoscedasticity.
            """
            )
            statistical_diff = paired_ttest(sample_a=sample_baseline_model, sample_b=sample_benchmark_model)
        else:
            st.markdown(
                """
            Either the samples do not follow a normal distribution or they do not have equal variances.
            Therefore, the **Wilcoxon signed-rank test** will be used. This is a non-parametric test appropriate
            when the assumptions of the t-test are not met.
            """
            )

            statistical_diff = wilcoxon_test(sample_a=sample_baseline_model, sample_b=sample_benchmark_model)

        st.markdown(
            f":red[**Results:**] The p-value obtained from the test was {statistical_diff.get('p-value'): .4e}. "
            f"{statistical_diff.get('interpretation')}"
        )
