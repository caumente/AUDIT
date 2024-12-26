import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.commons.strings import capitalizer
from src.utils.commons.strings import pretty_string
from src.visualization.constants import Dashboard

constants = Dashboard()


def multivariate_features(
    data, x_axis, y_axis, y_label=None, x_label=None, color="Dataset", log_x=False, log_y=False, legend_title=None
):

    if y_label is None:
        y_label = f"{pretty_string(y_axis)}"

    if x_label is None:
        x_label = f"{pretty_string(x_axis)}"

    # define the scatterplot
    if color == "Dataset":
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            color="set",
            custom_data=["ID", x_axis, y_axis],
            color_discrete_sequence=constants.discrete_color_palette,
            log_x=log_x,
            log_y=log_y,
        )
        fig.update_layout(legend_title=color, legend=dict(yanchor="top", xanchor="right"))
    else:
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            color=color,
            custom_data=["ID", x_axis, y_axis],
            color_continuous_scale=constants.continuous_color_palette,
            log_x=log_x,
            log_y=log_y,
        )
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=legend_title, y=0.5, x=1.05, len=0.85, yanchor="middle", xanchor="left", ticks="outside"
            )
        )

    # set up template
    fig.update_layout(template=constants.template, height=600, width=1000, xaxis_title=x_label, yaxis_title=y_label)

    # set up traces and markers
    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color="DarkSlateGrey")),
        selector=dict(mode="markers"),
        hovertemplate="ID: %{customdata[0]}<br>"
        f"{pretty_string(x_axis)}: " + "%{customdata[1]:,}<br>"
        f"{pretty_string(y_axis)}: " + "%{customdata[2]:,}",
    )

    return fig


def multivariate_features_highlighter(
    data,
    x_axis,
    y_axis,
    y_label=None,
    x_label=None,
    color="Dataset",
    log_x=False,
    log_y=False,
    legend_title=None,
    highlight_point=None,
):

    if y_label is None:
        y_label = f"{pretty_string(y_axis)}"

    if x_label is None:
        x_label = f"{pretty_string(x_axis)}"

    if legend_title is None:
        legend_title = f"{pretty_string(color)}"

    # define the scatterplot
    if color == "Dataset":
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            color="set",
            custom_data=["ID", x_axis, y_axis],
            color_discrete_sequence=constants.discrete_color_palette,
            log_x=log_x,
            log_y=log_y,
        )
        fig.update_layout(legend_title=legend_title, legend=dict(yanchor="top", xanchor="right"))
    else:
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            color=color,
            custom_data=["ID", x_axis, y_axis],
            color_continuous_scale=constants.continuous_color_palette,
            log_x=log_x,
            log_y=log_y,
        )
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=legend_title, y=0.5, x=1.05, len=0.85, yanchor="middle", xanchor="left", ticks="outside"
            )
        )

    # set up template
    fig.update_layout(template=constants.template, height=600, width=1000, xaxis_title=x_label, yaxis_title=y_label)

    if highlight_point is not None:
        point = data[data.ID == highlight_point]
        # Add a highlight trace for the specific point
        fig.add_trace(
            go.Scatter(
                x=point[x_axis],
                y=point[y_axis],
                customdata=point[["ID", x_axis, y_axis]].values.tolist(),
                mode="markers",
                showlegend=False,
                marker=dict(size=12, color="#e31231", symbol="circle", line=dict(width=1, color="DarkSlateGrey")),
                hoverlabel=dict(bordercolor="#444", font=dict(color="white"), bgcolor="#e31231"),
            )
        )

    # set up traces and markers
    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color="DarkSlateGrey")),
        selector=dict(mode="markers"),
        hovertemplate="ID: %{customdata[0]}<br>"
        f"{pretty_string(x_axis)}: " + "%{customdata[1]:,}<br>"
        f"{pretty_string(y_axis)}: " + "%{customdata[2]:,}<extra></extra>",
    )

    return fig


def multivariate_metric_feature(
    data: pd.DataFrame,
    x_axis: str,
    y_axis: str,
    y_label: str = None,
    x_label: str = None,
    color: str = "Dataset",
    facet_col: str = None,
    highlighted_subjects: list = None,
):

    if y_label is None:
        y_label = f"{pretty_string(y_axis)}"

    if x_label is None:
        x_label = f"{pretty_string(x_axis)}"

    color_axis = "set"
    if color != "Dataset":
        color_axis = color

    # Use a predefined Plotly color palette
    color_palette = constants.discrete_color_palette

    fig = px.scatter(
        data,
        x=x_axis,
        y=y_axis,
        color=color_axis,
        facet_col=facet_col,
        custom_data=["ID", x_axis, y_axis, data["model"].apply(pretty_string).apply(capitalizer)],
        color_discrete_sequence=color_palette,
    )

    fig.update_layout(
        template=constants.template,
        height=600,
        width=1000,
        showlegend=True,
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title=color,
        # legend=dict(yanchor="top", xanchor="right")
    )

    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color="DarkSlateGrey")),
        selector=dict(mode="markers"),
        hovertemplate="ID: %{customdata[0]}<br>"
        f"{x_label}: " + "%{customdata[1]:,.2f}<br>"
        f"{y_label}: " + "%{customdata[2]:,.3f}<br>"
        "Model: %{customdata[3]}",
    )

    # fig.for_each_yaxis(lambda y: pretty_string(y_label))

    # Highlight specific subjects
    if highlighted_subjects is not None:
        highlighted_data = data[data["ID"].isin(highlighted_subjects)]

        # Prepare custom data for hover template
        customdata = ["ID", x_axis, y_axis, highlighted_data["model"].apply(pretty_string).apply(capitalizer)]

        # Define marker properties
        marker_props = dict(size=12, line=dict(width=2, color="#444"), color="#e31231")

        # Define hover template
        hover_template = (
            "ID: %{customdata[0]}<br>"
            f"{x_label}:" + "%{customdata[1]:,.2f}<br>"
            f"{y_label}:" + "%{customdata[2]:,.3f}<br>"
            "Model: %{customdata[3]}"
        )

        # Define hover label properties
        hover_label_props = dict(bgcolor=["#e31231"], bordercolor="#444", font=dict(color="white"))

        # Create and add scatter plot traces
        scatter_plot = px.scatter(
            highlighted_data, x=x_axis, y=y_axis, facet_col=facet_col, custom_data=customdata
        ).update_traces(
            marker=marker_props,
            selector=dict(mode="markers"),
            hovertemplate=hover_template,
            hoverlabel=hover_label_props,
        )

        fig.add_traces(scatter_plot.data)

    return fig
