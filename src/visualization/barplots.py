import plotly.graph_objects as go

from src.utils.commons.strings import pretty_string
from src.visualization.constants import Dashboard

constants = Dashboard()


def aggregated_pairwise_model_performance(data, improvement_type, selected_metric, selected_set):
    units = ""
    if improvement_type == "relative":
        units = "%"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data[improvement_type],
            y=data["region"],
            orientation="h",
            marker_color=data["color_bar"],
            marker_line=dict(width=1, color="black"),
            hovertemplate=f"Improvement  {pretty_string(selected_metric)}: " + "%{x:.2f}" + f"{units}" + "<br>"
            "Region: %{y}<br>Dataset: " + selected_set,
        )
    )
    fig.update_xaxes(showline=False)
    fig.update_traces(width=constants.bar_width)
    fig.update_layout(template=constants.template, height=300, width=800, showlegend=False, margin=dict(b=20, t=20))

    return fig


def individual_pairwise_model_performance(data, baseline_model, benchmark_model, improvement_type):
    units = ""
    if improvement_type == "relative":
        units = "%"

    figures = []
    metric, set_ = data.metric.unique()[0], data.set.unique()[0]
    for case in data.ID.unique():
        df = data[data.ID == case]
        lesion_location = round(df["whole_tumor_location"].unique()[0], 2)
        lesion_size = df["lesion_size"].unique()[0]
        performance_baseline = float(df[baseline_model].unique()[0])
        performance_benchmark_model = float(df[benchmark_model].unique()[0])

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df[improvement_type],
                y=df["region"],
                orientation="h",
                marker_color=df["color_bar"],
                marker_line=dict(width=1, color="black"),
                hovertemplate="subject: "
                f"{case}"
                " <br>" + pretty_string(metric) + " : %{x:.2f}" + f"{units}<br>"
                "Region: %{y}<br>Dataset: " + set_,
            )
        )
        fig.update_xaxes(showline=False)
        fig.update_traces(width=constants.bar_width)
        fig.update_layout(
            template=constants.template,
            height=300,
            width=800,
            showlegend=False,
            xaxis_range=[data[improvement_type].min() - 0.5, data[improvement_type].max() + 0.5],
            margin=dict(b=20, t=60),
            title=f"Subject: {case} - "
            f"Lesion location: {lesion_location}mm - "
            f"Lesion size: {lesion_size:,} voxels<br>"
            f"Average performance baseline: {performance_baseline:.3f} - "
            f"Avergage performance benchmark model: {performance_benchmark_model:.3f}",
        )

        figures.append(fig)

    return figures
