import streamlit as st

from src.app.util.constants.features import Features
from src.app.util.constants.metrics import Metrics
from src.utils.commons.strings import pretty_string

# Load constants
const_metrics = Metrics()
metrics_dict = const_metrics.get_metrics()
orderby_dict = const_metrics.orderby
const_features = Features()


def setup_sidebar_multi_datasets(data_paths):
    with st.sidebar.expander("Datasets", expanded=True):
        selected_sets = st.multiselect(
            label="Select datasets to visualize:",
            options=data_paths.keys(),
            default=data_paths.keys()
        )
    return selected_sets


def setup_sidebar_single_dataset(data):
    with st.sidebar.expander("Datasets", expanded=True):
        selected_set = st.selectbox("Select dataset to analyze:", options=list(data.set.unique()), index=0)

    return selected_set


def setup_sidebar_single_metric(data):
    available_metrics = [k for k, v in metrics_dict.items() if v in data.columns]
    with st.sidebar.expander("Metrics", expanded=True):
        selected_metric = st.selectbox("Select metric to analyze:", options=available_metrics, index=0)

    return selected_metric


def setup_sidebar_multi_metrics(data):
    available_metrics = [k for k, v in metrics_dict.items() if v in data.columns]
    with st.sidebar.expander("Metrics", expanded=True):
        selected_metrics = st.multiselect(
            label="Select metrics to analyze:",
            options=available_metrics,
            default=available_metrics[0]
        )

    return selected_metrics


def setup_sidebar_single_model(data):
    with st.sidebar.expander("Models", expanded=True):
        selected_model = st.selectbox("Select model to analyze:", options=list(data.model.unique()), index=0)

    return selected_model


def setup_sidebar_multi_model(data):
    with st.sidebar.expander("Models", expanded=True):
        selected_models = st.multiselect(
            label="Select models to analyze:",
            options=list(data.model.unique()),
            default=list(data.model.unique())
        )

    return selected_models


def setup_sidebar_pairwise_models(data, selected_set):
    with st.sidebar.expander("Models", expanded=True):
        # models_available = [capitalizer(pretty_string(m)) for m in data[data.set == selected_set].model.unique()]
        models_available = data[data.set == selected_set].model.unique()
        baseline_model = st.selectbox("Select the baseline model:", options=models_available, index=0)
        benchmark_model = st.selectbox("Select the benchmark model:", options=models_available, index=1)
        if baseline_model == benchmark_model:
            st.error("Models selected must be different to make a performance comparison", icon="🚨")

    return baseline_model, benchmark_model


def setup_sidebar_features(data, name, c_index=0, f_index=0, key=None):
    with st.sidebar.expander(name, expanded=True):
        select_category = st.selectbox(
            label="Feature category:",
            options=const_features.categories,
            index=c_index,
            key=f"c_{key}"
        )
        available_features = [k for k, v in const_features.get_features(select_category).items() if v in data.columns]
        selected_feature = st.selectbox(
            label="Feature name:",
            options=available_features,
            index=f_index,
            key=f"f_{key}"
        )
        selected_feature = const_features.get_features(select_category).get(selected_feature, None)

    return selected_feature


def setup_sidebar_color(data, name, c_index=0, f_index=0, key=None):
    with st.sidebar.expander(name, expanded=True):
        select_color_category = st.selectbox(
            label="Feature category:",
            options=["Dataset"] + const_features.categories,
            index=c_index,
            key=f"c_{key}"
        )

        if select_color_category == "Dataset":
            select_color_axis = 'Dataset'
        else:
            available_features = [k for k, v in const_features.get_features(select_color_category).items() if
                                  v in data.columns]
            select_color_axis = st.selectbox(
                label="Feature name:",
                options=available_features,
                index=f_index,
                key=f"f_{key}"
            )
            select_color_axis = const_features.get_features(select_color_category).get(select_color_axis, None)

    return select_color_axis


def setup_highlight_subject(data):
    with st.sidebar.expander(label="Highlight subject"):
        selected_sets = st.selectbox(
            label="Dataset:", options=data.set.unique(), index=0
        )

        highlight_subject = st.selectbox(
            label="Enter subject ID to highlight",
            options=[None] + list(data[data.set == selected_sets].ID.unique()),
            index=0
        )

    return highlight_subject


def setup_histogram_options(plot_type):
    """
    Set up histogram customization options based on plot type.

    Args:
        plot_type (str): Type of plot ("Histogram" or "Probability").

    Returns:
        tuple: Number of bins or bin size based on user selection.
    """
    n_bins, bins_size = None, None
    if plot_type == "Histogram":
        with st.sidebar.expander("Customization", expanded=True):
            option = st.selectbox("Define number of bins or bins size", ("Number of bins", "Bins size"))
            if option == "Number of bins":
                n_bins = st.number_input(
                    "Select the number of bins",
                    min_value=1,
                    max_value=200,
                    value=100,
                    step=1,
                    placeholder="Type a number...",
                    help="The actual number of bins will be the closest value to your selection based on distribution.",
                )
            elif option == "Bins size":
                bins_size = st.number_input(
                    "Select bins size", min_value=1, max_value=None, value=1, step=1, placeholder="Type a number..."
                )

    return n_bins, bins_size


def setup_filtering_options(df, feature):
    """
    Set up filtering options based on selected features.

    Args:
        df (DataFrame): DataFrame containing the data.
        feature (dict): Feature selected

    Returns:
        tuple: Filtering method and corresponding parameters.
    """
    with st.sidebar.expander("Filtering", expanded=False):
        filtering_method = st.radio(
            label="Filter data based on",
            options=["No filter", "Removing outliers", "Clipping outliers", "Standard deviations"],
            captions=[
                "",
                "It remove values outside a specified range",
                "It restricts the range of data by capping values below and above a threshold to the lower "
                "and upper bound selected.",
                "Filtering data based on standard deviations",
            ],
        )

        remove_low, remove_up = None, None
        clip_low, clip_up = None, None
        num_std_devs = None

        if filtering_method == "Removing outliers":
            remove_low, remove_up = st.slider(
                "Remove outliers within a range of values",
                min_value=df[feature].min(),
                max_value=df[feature].max(),
                value=(df[feature].min(), df[feature].max()),
            )
        elif filtering_method == "Clipping outliers":
            clip_low, clip_up = st.slider(
                "Clip outliers within a range of values",
                min_value=df[feature].min(),
                max_value=df[feature].max(),
                value=(df[feature].min(), df[feature].max()),
            )
        elif filtering_method == "Standard deviations":
            # mean, std_dev = df[feature].mean(), df[feature].std()
            num_std_devs = st.number_input(label="Number of standard deviations", min_value=1, step=1, value=3)

    return filtering_method, remove_low, remove_up, clip_low, clip_up, num_std_devs


def setup_metrics_customization(baseline_model, benchmark_model, aggregated):
    mapping_performance = {
                f"subject ID": "ID",
                f"Performance ({baseline_model})": f"{baseline_model}",
                f"Performance ({benchmark_model})": f"{benchmark_model}",
                }
    num_max_subjects, selected_sorted, selected_order = None, None, None
    if not aggregated:
        with st.sidebar.expander("Customization", expanded=True):
            num_max_subjects = st.number_input("Maximum subjects to visualize", min_value=1, value=5, step=1)
            mapping_buttons_columns_perf = {
                **const_features.get_multiple_features(["common"]).copy(),
                **mapping_performance,
            }
            selected_sorted = st.selectbox("Sorted by:", options=mapping_buttons_columns_perf)
            selected_order = st.radio("Order by:", options=orderby_dict.keys())

    return num_max_subjects, mapping_performance.get(selected_sorted), orderby_dict.get(selected_order)


def setup_improvement_button():
    improvement_type = st.selectbox(
        label="Type of comparison",
        options=["relative", "absolute", "ratio"],
        format_func=pretty_string,
        index=0
    )
    return improvement_type


def setup_aggregation_button():
    return st.checkbox("Aggregated.", value=True, help="It aggregates all the subjects, if enabled.")


def setup_clip_sidebar(data, feature):
    clip_low, clip_up = None, None
    with st.sidebar:
        metric_clip = st.checkbox(
            "Clip the metric",
            help="It restricts the range of the metrics by capping values below and "
                 "above a threshold to the lower and upper bound selected, if "
                 "enabled.",
        )

        if metric_clip:
            clip_low, clip_up = st.slider(
                label="Clip metric",
                min_value=data[feature].min(),
                max_value=data[feature].max(),
                value=(data[feature].min(), data[feature].max()),
                label_visibility="collapsed",
            )

    return clip_low, clip_up


def setup_statistical_test():
    statistical_test = st.checkbox(
        label="Perform statistical test",
        help="It performs statistical tests to evaluate whether exist statistical "
             "differences between the model performance, if enabled.",
    )

    return statistical_test


def setup_button_data_download(df):
    st.download_button(
        label="Download data used in the statistical tests as CSV",
        data=df.to_csv().encode("utf-8"),
        file_name="raw_data_statistical_test.csv",
        mime="text/csv",
    )


def setup_sidebar_regions(data, aggregated):
    selected_regions = None
    if not aggregated:
        with st.sidebar.expander("Regions", expanded=True):
            available_regions = list(data.region.unique())
            selected_regions = st.multiselect(
                label="Select the regions to visualize:",
                options=available_regions,
                default=available_regions
            )

    return selected_regions


def setup_sidebar_longitudinal_subject(data):
    with st.sidebar.expander("Subjects", expanded=True):
        subject_selected = st.selectbox(
            label="Select a subject to visualize:",
            options=sorted(data.longitudinal_id.unique()),
            index=0
        )

    return subject_selected


def setup_sidebar_single_subjects(data):
    with st.sidebar.expander("Subjects", expanded=True):
        subject_selected = st.selectbox(
            label="Select a subject to visualize:",
            options=sorted(data.ID.unique()),
            index=0
        )

    return subject_selected
