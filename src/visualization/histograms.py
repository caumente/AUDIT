import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from scipy.stats import iqr

from src.utils.commons.strings import pretty_string
from src.visualization.constants import Dashboard

constants = Dashboard()


def optimal_num_bins(data: np.array) -> int:
    """
    Calculate the optimal number of bins for a histogram using the Freedman-Diaconis rule.

    Parameters:
    data (array-like): The input data for which the optimal number of bins is to be calculated.

    Returns:
    float: The optimal number of bins for the given data.
    """

    return int(2 * iqr(data) * len(data) ** (-1 / 3))


def plot_histogram(data, x_axis, color_var, n_bins, y_label=None, x_label=None):

    if y_label is None:
        y_label = "Count"

    if x_label is None:
        x_label = f"{pretty_string(x_axis)}"

    fig = px.histogram(data, x=x_axis, color=color_var, hover_data=data.columns, nbins=n_bins, barmode="stack")

    fig.update_layout(
        template=constants.template,
        height=500,
        width=900,
        showlegend=True,
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title="Dataset",
    )
    fig.update_traces(opacity=0.6)

    return fig


def custom_histogram(data, x_axis, color_var, n_bins, bins_size=None, y_label=None, x_label=None):

    if bins_size:
        n_bins = None

    if y_label is None:
        y_label = "Count"

    if x_label is None:
        x_label = f"{pretty_string(x_axis)}"

    if not bins_size:
        # Compute bin size
        bin_size = (data[x_axis].max() - data[x_axis].min()) / n_bins

    # Use a predefined Plotly color palette
    color_palette = constants.discrete_color_palette

    # Map each unique value in color_var to a color from the palette
    unique_values = data[color_var].unique()
    color_map = {value: color_palette[i % len(color_palette)] for i, value in enumerate(unique_values)}

    # Create histogram for each color category
    fig = go.Figure()

    for n, color_value in enumerate(data[color_var].unique()):
        filtered_data = data[data[color_var] == color_value][x_axis]
        if not filtered_data.isnull().all():
            fig.add_trace(
                go.Histogram(
                    x=filtered_data,
                    name=color_value,
                    marker=dict(color=color_map[color_value], line=dict(width=0.8, color="black")),
                    autobinx=False,
                )
            )

    # Update layout for stacked histogram
    fig.update_layout(
        template=constants.template,
        height=400,
        width=900,
        showlegend=True,
        margin=dict(t=20, b=0),
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title="Dataset",
        barmode="stack",
        legend=dict(yanchor="top", xanchor="right",),
    )

    if bins_size:
        fig.update_traces(opacity=0.6, xbins_size=bins_size)
    else:
        fig.update_traces(opacity=0.6, xbins=dict(start=data[x_axis].min(), end=data[x_axis].max(), size=bin_size))

    # fig.update_traces(marker_line_width=1, marker_line_color="Black")

    return fig


def custom_distplot(data, x_axis, color_var, y_label=None, x_label=None, histnorm="probability"):
    """
    - probability density': Normalizes the histogram so that the area under the curve sums to 1, converting the counts
                            to probability densities. This is useful for comparing distributions with different sample
                            sizes.
    - probability': Normalizes the histogram so that the sum of all bars equals 1, meaning each bar represents the
                    probability of the data falling within that bin. This is useful for visualizing the distribution of
                    data in terms of probability.


    Probability Density: The heights of the bars indicate the probability density. The total area of all bars is 1.
    Probability: The heights of the bars indicate the probability. The sum of the heights of all bars is 1
    """

    if y_label is None:
        y_label = "Density"

    if x_label is None:
        x_label = f"{pretty_string(x_axis)}"

    # Use a predefined Plotly color palette
    color_palette = constants.discrete_color_palette

    # Map each unique value in color_var to a color from the palette
    unique_values = data[color_var].unique()
    color_map = {value: color_palette[i % len(color_palette)] for i, value in enumerate(unique_values)}

    # Collect data for each color category
    hist_data = []
    group_labels = []
    colors = []

    for color_value in unique_values:
        filtered_data = data[data[color_var] == color_value][x_axis]
        if not filtered_data.isnull().all():
            hist_data.append(filtered_data[~np.isnan(filtered_data)])  # removing nan values
            group_labels.append(color_value)
            colors.append(color_map[color_value])

    opt_bins = optimal_num_bins(np.concatenate(hist_data))

    # Create distplot
    fig = ff.create_distplot(
        hist_data,
        group_labels,
        bin_size=opt_bins,
        show_hist=False,
        show_rug=False,
        colors=colors,
        histnorm=histnorm,
        curve_type="kde",
    )  # histnorm='probability density'

    # Update layout
    fig.update_layout(
        template=constants.template,
        height=400,
        width=900,
        showlegend=True,
        margin=dict(t=20, b=0),
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title="Dataset",
        legend=dict(yanchor="top", xanchor="right",),
        xaxis=dict(color="black", title_font=dict(color="black", size=16), tickfont=dict(color="black", size=14)),
        yaxis=dict(color="black", title_font=dict(color="black", size=16), tickfont=dict(color="black", size=14)),
    )

    fig.update_traces(line={"width": 3})

    return fig
