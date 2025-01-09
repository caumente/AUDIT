import pandas as pd
import streamlit as st

from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.commons.sidebars import setup_aggregation_button
from audit.app.util.commons.sidebars import setup_sidebar_multi_metrics
from audit.app.util.commons.sidebars import setup_sidebar_multi_model
from audit.app.util.commons.sidebars import setup_sidebar_regions
from audit.app.util.commons.sidebars import setup_sidebar_single_dataset
from audit.app.util.commons.utils import download_plot
from audit.app.util.constants.descriptions import MultiModelPerformanceComparisonsPage
from audit.app.util.constants.metrics import Metrics
from audit.utils.commons.file_manager import load_config_file
from audit.utils.commons.file_manager import read_datasets_from_dict
from audit.visualization.boxplot import models_performance_boxplot

const_descriptions = MultiModelPerformanceComparisonsPage()
const_metrics = Metrics()
metrics_dict = const_metrics.get_metrics()


def setup_sidebar(data):
    with st.sidebar:
        st.header("Configuration")

        selected_set = setup_sidebar_single_dataset(data)
        selected_models = setup_sidebar_multi_model(data)
        selected_regions = setup_sidebar_regions(data, aggregated=False)
        selected_metrics = setup_sidebar_multi_metrics(data)
        selected_metrics = [metrics_dict.get(m) for m in selected_metrics]

    return selected_set, selected_models, selected_regions, selected_metrics


def visualize_data(data, agg):
    # Show the plot
    st.markdown(const_descriptions.description)
    fig = models_performance_boxplot(data, aggregated=agg)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    download_plot(fig, label="Models performance", filename="multimodel_performance")


def main_table(data, aggregate):
    # postprocessing data
    data.rename(columns={v: k for k, v in metrics_dict.items()}, inplace=True)
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


def multi_model(config):
    # load config files
    metrics_paths = config.get("metrics")
    features_paths = config.get("features")

    # Defining page
    st.subheader(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)

    # Load the data
    raw_metrics = read_datasets_from_dict(metrics_paths)
    agg = setup_aggregation_button()

    # calling main function
    selected_set, selected_models, selected_regions, selected_metrics = setup_sidebar(raw_metrics)

    df = processing_data(
        data=raw_metrics,
        models=selected_models,
        sets=selected_set,
        regions=selected_regions,
        features=["ID", 'region', 'model', 'set'] + selected_metrics
    )

    data_melted = main_table(df, agg)

    visualize_data(data_melted, agg)
