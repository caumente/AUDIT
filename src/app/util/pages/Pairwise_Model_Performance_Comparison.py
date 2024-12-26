import numpy as np
import pandas as pd
import streamlit as st

from src.app.util.commons.checks import models_sanity_check
from src.app.util.commons.data_preprocessing import processing_data
from src.app.util.commons.sidebars import setup_aggregation_button
from src.app.util.commons.sidebars import setup_button_data_download
from src.app.util.commons.sidebars import setup_clip_sidebar
from src.app.util.commons.sidebars import setup_improvement_button
from src.app.util.commons.sidebars import setup_metrics_customization
from src.app.util.commons.sidebars import setup_sidebar_pairwise_models
from src.app.util.commons.sidebars import setup_sidebar_single_dataset
from src.app.util.commons.sidebars import setup_sidebar_single_metric
from src.app.util.commons.sidebars import setup_statistical_test
from src.app.util.commons.utils import download_plot
from src.app.util.constants.descriptions import PairwiseModelPerformanceComparisonPage
from src.app.util.constants.features import Features
from src.app.util.constants.metrics import Metrics
from src.metrics.commons import calculate_improvements
from src.metrics.statistical_tests import normality_test
from src.metrics.statistical_tests import paired_ttest
from src.metrics.statistical_tests import wilcoxon_test
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.file_manager import read_datasets_from_dict
from src.visualization.barplots import aggregated_pairwise_model_performance
from src.visualization.barplots import individual_pairwise_model_performance
from src.visualization.histograms import plot_histogram

# Load constants
const_descriptions = PairwiseModelPerformanceComparisonPage()
const_metrics = Metrics()
metrics_dict = const_metrics.get_metrics()
orderby_dict = const_metrics.orderby
const_features = Features()

# Load configuration files
config = load_config_file("./src/configs/app.yml")
metrics_paths = config.get("metrics")
features_paths = config.get("features")


def setup_sidebar(data, aggregated=True):
    with st.sidebar:
        st.header("Configuration")

        selected_set = setup_sidebar_single_dataset(data)
        baseline_model, benchmark_model = setup_sidebar_pairwise_models(data, selected_set)
        selected_metric = setup_sidebar_single_metric(data)
        num_max_subjects, selected_sorted, selected_order = setup_metrics_customization(baseline_model, benchmark_model, aggregated)

    return selected_set, baseline_model, benchmark_model, selected_metric, num_max_subjects, selected_sorted, selected_order


def process_metrics(data, selected_metric, baseline_model, benchmark_model, aggregate=False, improvement_type="Absolute"):
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
        averages['region'] = 'Average'
    else:
        averages = pivot_df.groupby("ID").mean(numeric_only=True).reset_index()
        averages['region'] = 'Average'
    pivot_df = pd.concat([pivot_df, averages], ignore_index=True)

    # computing improvements
    out = calculate_improvements(pivot_df, baseline_model, benchmark_model)
    out["metric"] = selected_metric
    out["color_bar"] = np.where(out[improvement_type] < 0, const_descriptions.colorbar.get("decrease"), const_descriptions.colorbar.get("increase"))

    return out


def run_individualized(data, baseline_model, benchmark_model, improvement_type, selected_sorted, selected_order, num_max_subjects):
    # Sort dataset
    l = data[data.region == 'Average'].sort_values(by=selected_sorted, ascending=selected_order)['ID']
    data['ID'] = pd.Categorical(data['ID'], categories=l, ordered=True)
    data = data.sort_values(['ID', 'region'])

    # Filter based on the number of subjects
    if num_max_subjects:
        data = data[data.ID.isin(l[:num_max_subjects])]

    # Clip metric
    clip_low, clip_up = setup_clip_sidebar(data, improvement_type)
    if clip_low is not None and clip_up is not None:
        data[improvement_type] = data[improvement_type].clip(clip_low, clip_up)

    all_figures = individual_pairwise_model_performance(data, baseline_model, benchmark_model, improvement_type)
    for fig in all_figures:
        st.plotly_chart(fig, theme="streamlit", use_container_width=False, scrolling=True)


def run_aggregated(data, improvement_type, selected_metric, selected_set):
    fig = aggregated_pairwise_model_performance(data, improvement_type, selected_metric, selected_set)
    st.plotly_chart(fig, theme="streamlit", use_container_width=False, scrolling=True)
    download_plot(fig, label="Aggregated Pairwise Model Performance", filename="agg_pairwise_model_performance")


def visualize_histogram(data, model):
    fig = plot_histogram(
        data=data[[model]],
        x_axis=model,
        color_var=None,
        n_bins=10,
        x_label=None,
    )

    return fig


def perform_normality_test(data, selected_set, selected_metric, baseline_model, benchmark_model):
    st.markdown("""**Performing normality test:**""")
    col1, col2 = st.columns(2)
    df_wide = data[data.set == selected_set][["ID", "model", metrics_dict.get(selected_metric, None)]]
    df_wide = df_wide.pivot(index="ID", columns="model", values=metrics_dict.get(selected_metric, None))

    sample_baseline_model = df_wide[baseline_model]
    sample_benchmark_model = df_wide[benchmark_model]

    with col1:
        # checking normality baseline model
        normality_test_bas_model = normality_test(sample_baseline_model)
        st.table(pd.DataFrame(normality_test_bas_model.items(), columns=["Metric", "Baseline model"]).set_index("Metric"))
        st.plotly_chart(visualize_histogram(df_wide, baseline_model), theme="streamlit", use_container_width=True, scrolling=True)

    with col2:
        # checking normality benchmark model
        normality_test_ben_model = normality_test(sample_benchmark_model)
        st.table(pd.DataFrame(normality_test_ben_model.items(), columns=["Metric", "Benchmark model"]).set_index("Metric"))
        st.plotly_chart(visualize_histogram(df_wide, benchmark_model), theme="streamlit", use_container_width=True, scrolling=True)

    return sample_baseline_model, sample_benchmark_model, normality_test_bas_model, normality_test_ben_model


def perform_statistical_test(
    normality_test_baseline_model, normality_test_benchmark_model, sample_baseline_model, sample_benchmark_model
):
    st.markdown("""**Performing statistical test:**""")
    if normality_test_baseline_model["Normally distributed"] and normality_test_benchmark_model["Normally distributed"]:
        st.markdown("""
        Both the baseline model sample and the benchmark model sample follow a normal distribution.
        Therefore, the **Paired Student t-test** will be performed. This is a parametric test that compares two
        **paired samples** normally distributed.""")

        statistical_diff = paired_ttest(sample1=sample_baseline_model, sample2=sample_benchmark_model)
    else:
        st.markdown("""
        Either the baseline model sample or the benchmark model sample does not follow a normal distribution.
        Therefore, the **Wilcoxon signed-rank test** will be used. This is a non-parametric test that compares two
        **paired samples** when normality cannot be assumed.
        """)

        statistical_diff = wilcoxon_test(sample1=sample_baseline_model, sample2=sample_benchmark_model)

    st.markdown(
        f":red[**Results:**] The p-value obtained from the test was {statistical_diff.get('p-value'): .4e}. "
        f"{statistical_diff.get('interpretation')}"
    )


def pairwise_comparison():

    # Defining page
    st.subheader(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)
    show_descriptions = st.toggle("Show formulas")
    if show_descriptions:
        st.markdown(const_descriptions.description)
        st.latex(const_descriptions.absolute_formula)
        st.latex(const_descriptions.relative_formula)
        st.latex(const_descriptions.ratio_formula)

    # type of improvement and aggregation
    improvement_type = setup_improvement_button()
    agg = setup_aggregation_button()

    # Load datasets
    raw_metrics = read_datasets_from_dict(metrics_paths)
    raw_features = read_datasets_from_dict(features_paths)
    df_stats = raw_metrics.drop(columns="region").groupby(["ID", "model", "set"]).mean().reset_index()

    # Setup sidebar
    selected_set, ba_model, be_model, selected_metric, num_subjects, selected_sorted, selected_order = setup_sidebar(raw_metrics, agg)

    if not models_sanity_check(ba_model, be_model):
        st.error("Models selected must be different to make a performance comparison", icon="🚨")
    else:
        df = processing_data(raw_metrics, selected_set, features=['ID', 'region', metrics_dict.get(selected_metric, None), 'model', 'set'])
        df = process_metrics(
            data=df.drop(columns='set'),
            selected_metric=metrics_dict.get(selected_metric, None),
            baseline_model=ba_model,
            benchmark_model=be_model,
            aggregate=agg,
            improvement_type=improvement_type
        )

        # Merge with features and average performance if not aggregated
        if not agg:
            df = df.merge(raw_features, on=["ID"])
            run_individualized(df, ba_model, be_model, improvement_type, selected_sorted, selected_order, num_subjects)
        else:
            run_aggregated(df, improvement_type, selected_metric, selected_set)

            # Perform statistical test
            if setup_statistical_test():
                sample_bm, sample_nm, nt_baseline_model, nt_benchmark_model = perform_normality_test(
                    df_stats, selected_set, selected_metric, ba_model, be_model
                )

                perform_statistical_test(nt_baseline_model, nt_benchmark_model, sample_bm, sample_nm)

                setup_button_data_download(df_stats)
