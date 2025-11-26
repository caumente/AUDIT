import plotly.graph_objects as go
from plotly.colors import qualitative

from audit.utils.commons.strings import pretty_string
from audit.visualization.constants import Dashboard

constants = Dashboard()


# def plot_longitudinal(data, temporal_axis="time_point", lines=["lesion_size_whole", "lesion_size_pred"]):
#     fig = go.Figure()
#
#     colors = qualitative.Pastel
#     custom_labels = ["Actual lesion size", "Predicted lesion size"]
#
#     for n, l in enumerate(lines):
#         fig.add_trace(
#             go.Scatter(
#                 x=data[temporal_axis],
#                 y=data[l],
#                 mode="markers+lines",
#                 name=custom_labels[n],
#                 line=dict(color=colors[n], width=3),
#                 marker=dict(color=colors[n], size=8),
#                 hoverinfo="skip",
#             )
#         )
#
#     # Add vertical dashed lines to measure the distance between points and add annotation for distance
#     hover_data = []
#     for i in range(len(data)):
#         lesion_size = data[lines[0]][i]
#         lesion_size_pred = data[lines[1]][i]
#         distance = 100 * (lesion_size - lesion_size_pred) / lesion_size
#         mid_y = (lesion_size + lesion_size_pred) / 2
#         hover_data.append(
#             f"<b>Timepoint:</b> {data[temporal_axis][i]}<br>"
#             f"<b>Actual lesion size:</b> {lesion_size:.2f} mm³<br>"
#             f"<b>Predicted lesion size:</b> {lesion_size_pred:.2f} mm³<br>"
#             f"<b>Difference (%):</b> {distance:.1f}%<extra></extra>"
#         )
#
#         fig.add_trace(
#             go.Scatter(
#                 x=[data[temporal_axis][i], data[temporal_axis][i]],
#                 y=[lesion_size, lesion_size_pred],
#                 mode="lines",
#                 line=dict(color=colors[len(lines)], dash="dot", width=2),
#                 showlegend=False,
#                 hovertext=hover_data,
#                 hoverinfo="text",
#             )
#         )
#
#         # Add annotation for the distance
#         fig.add_annotation(
#             x=data[temporal_axis][i],
#             y=mid_y,
#             text=f"{distance:.1f}%",
#             showarrow=False,
#             font=dict(color=colors[len(lines)], size=16),
#         )
#
#     # Layout general
#     fig.update_layout(
#         title="Longitudinal Analysis of Lesion Sizes",
#         light_theme=constants.light_theme,
#         height=600,
#         width=1000,
#         xaxis_title=pretty_string(temporal_axis),
#         yaxis_title="Lesion Size (mm<sup>3</sup>)",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.7),
#     )
#     fig.update_xaxes(tickmode="linear", dtick=1, tickformat=",d")
#
#     return fig
#
#
# def plot_longitudinal2(data, temporal_axis="time_point", lines=["lesion_size_whole", "lesion_size_pred"]):
#     fig = go.Figure()
#
#     colors = qualitative.Pastel
#     custom_labels = ["Actual lesion size", "Predicted lesion size"]
#
#     for n, l in enumerate(lines):
#         fig.add_trace(
#             go.Scatter(
#                 x=data[temporal_axis],
#                 y=data[l],
#                 mode="markers+lines",
#                 name=custom_labels[n],
#                 line=dict(color=colors[n], width=3),
#                 marker=dict(color=colors[n], size=8),
#             )
#         )
#
#     # add lines to measure the distance between points and calculate the difference in slopes
#     for i in range(len(data) - 1):
#         x1, x2 = data[temporal_axis][i], data[temporal_axis][i + 1]
#         actual_volume_t0, actual_volume_t1 = data[lines[0]][i], data[lines[0]][i + 1]
#         pred_volume_t0, pred_volume_t1 = data[lines[1]][i], data[lines[1]][i + 1]
#
#         pred_growth_tumor_ratio = (pred_volume_t1 - pred_volume_t0) / pred_volume_t0
#         actual_growth_tumor_ratio = (actual_volume_t1 - actual_volume_t0) / actual_volume_t0
#         difference = actual_growth_tumor_ratio - pred_growth_tumor_ratio
#
#         mid_x = (x1 + x2) / 2
#         mid_y = (actual_volume_t0 + actual_volume_t1 + pred_volume_t0 + pred_volume_t1) / 4  # To place the annotation approximately in the middle
#
#         # Add annotation for the calculated difference
#         fig.add_annotation(
#             x=mid_x,
#             y=mid_y,
#             text=f"{difference:.2f}",
#             showarrow=False,
#             arrowhead=2,
#             ax=0,
#             ay=-20,
#             font=dict(color=colors[n + 1], size=16),
#         )
#
#     fig.update_layout(
#         light_theme=constants.light_theme,
#         height=600,
#         width=1000,
#         xaxis_title=pretty_string(temporal_axis),
#         yaxis_title="Lesion size (mm<sup>3</sup>)",
#         title="",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.7),
#         hovermode="x unified",
#     )
#     fig.update_xaxes(tickmode="linear", dtick=1, tickformat=",d")
#
#     return fig
#
#
# def plot_longitudinal3(data, temporal_axis="time_point", lines=["lesion_size_whole", "lesion_size_pred"]):
#     fig = go.Figure()
#
#     colors = qualitative.Pastel
#     custom_labels = ["Actual lesion size", "Predicted lesion size"]
#
#     for n, l in enumerate(lines):
#         fig.add_trace(
#             go.Scatter(
#                 x=data[temporal_axis],
#                 y=data[l],
#                 mode="markers+lines",
#                 name=custom_labels[n],
#                 line=dict(color=colors[n], width=3),
#                 marker=dict(color=colors[n], size=8),
#             )
#         )
#
#     # add lines to measure the distance between points and calculate the difference in slopes
#     for i in range(len(data) - 1):
#         x1, x2 = data[temporal_axis][i], data[temporal_axis][i + 1]
#         actual_volume_t0, actual_volume_t1 = data[lines[0]][i], data[lines[0]][i + 1]
#         pred_volume_t0, pred_volume_t1 = data[lines[1]][i], data[lines[1]][i + 1]
#
#         actual_tumor_growth = actual_volume_t1 - actual_volume_t0
#         pred_tumor_growth = pred_volume_t1 - pred_volume_t0
#         difference = actual_tumor_growth / pred_tumor_growth
#
#         mid_x = (x1 + x2) / 2
#         mid_y = (actual_volume_t0 + actual_volume_t1 + pred_volume_t0 + pred_volume_t1) / 4  # To place the annotation approximately in the middle
#
#         # Add annotation for the calculated difference
#         fig.add_annotation(
#             x=mid_x,
#             y=mid_y,
#             text=f"{difference:.2f}",
#             showarrow=False,
#             arrowhead=2,
#             ax=0,
#             ay=-20,
#             font=dict(color=colors[n + 1], size=16),
#         )
#
#     fig.update_layout(
#         light_theme=constants.light_theme,
#         height=600,
#         width=1000,
#         xaxis_title=pretty_string(temporal_axis),
#         yaxis_title="Lesion size (mm<sup>3</sup>)",
#         title="",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.7),
#         hovermode="x unified",
#     )
#     fig.update_xaxes(tickmode="linear", dtick=1, tickformat=",d")
#
#     return fig


# Plot multiple lines with markers and customized colors
def plot_lines_with_markers(df, x_col, line_cols, colors):
    fig = go.Figure()
    custom_labels = ["Observed Lesion Size", "Predicted Lesion Size"]

    for i, col in enumerate(line_cols):
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="lines+markers",
                name=custom_labels[i],
                line=dict(color=colors[i], width=3),
                marker=dict(color=colors[i], size=8),
                hoverinfo="text",
                hovertext=[f"{custom_labels[i]}: {int(y_val):,}" for y_val in df[col]]
                # hovertext=f"%{custom_labels[i]}: %{y:.0f}%"
            )
        )

    fig.update_layout(
        title="Lesion Size Analysis",
        xaxis_title=x_col.capitalize(),
        yaxis_title="Lesion Size (mm³)",
        legend_title="Legend",
        template="plotly_white",
    )
    return fig


# Add annotations for percentage difference between observed and predicted values
def add_percentage_differences(df, x_col, line_cols, fig, color="#005f73"):
    x_vals = df[x_col]
    y_observed = df[line_cols[0]]
    y_predicted = df[line_cols[1]]

    for i in range(len(x_vals)):
        # Calculate percentage difference
        diff_pct = ((y_predicted[i] - y_observed[i]) / y_observed[i]) * 100

        # Add a dashed line connecting observed and predicted values
        fig.add_trace(
            go.Scatter(
                x=[x_vals[i], x_vals[i]],
                y=[y_observed[i], y_predicted[i]],
                mode="lines",
                name=f"Relative difference in size estimation (%): {diff_pct}",
                line=dict(dash="dot", color=color, width=1),
                showlegend=False,
                hoverinfo="text",
                hovertext=f"Relative difference: {diff_pct:.1f}%",
            )
        )

        # Add percentage difference as text annotation
        fig.add_trace(
            go.Scatter(
                x=[x_vals[i]],
                y=[(y_observed[i] + y_predicted[i]) / 2],
                mode="text",
                text=[f"{diff_pct:.0f}%"],
                showlegend=False,
                textfont=dict(color=color, size=12, family="Arial Black"),
                hoverinfo="skip",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[None],  # Placeholder for legend only
            y=[None],
            mode="lines",
            line=dict(dash="dot", color=color, width=3),  # Wider line for legend
            name="Relative difference in size estimation",
            showlegend=True,
            hoverinfo="skip",
        )
    )
    return fig


# Add annotations for tumor growth percentage between time points
def add_tumor_growth_annotations(df, x_col, line_cols, fig, colors=["#9c5c2a", "#8a6b1e"]):
    def calculate_growth_and_positions(column):
        growth = [
            (df[column].iloc[i] - df[column].iloc[i - 1]) / df[column].iloc[i - 1] for i in range(1, len(df[column]))
        ]
        y_positions = [(df[column].iloc[i] + df[column].iloc[i - 1]) / 2 for i in range(1, len(df[column]))]
        return growth, y_positions

    for col, color, custom_label in zip(line_cols, colors, ["Observed tumor growth", "Predicted tumor growth"]):
        growth_rates, y_positions = calculate_growth_and_positions(col)
        x_positions = (df[x_col].iloc[1:].values + df[x_col].iloc[:-1].values) / 2

        for i, (x, y, text) in enumerate(zip(x_positions, y_positions, growth_rates)):
            fig.add_trace(
                go.Scatter(
                    x=[x],
                    y=[y],
                    mode="text",
                    text=[f"{text * 100:.0f}%"],
                    name="Tumor growth",
                    marker=dict(color=color),
                    showlegend=False,
                    # textfont=dict(color='#38413f', size=13, family="Arial Black")
                    textfont=dict(color=color, size=13, family="Arial Black"),
                    # hovertext=[f"Tumor growth: {float(100*text):.1f}%"],
                    hovertext=[f"{custom_label}: {float(100*text):.1f}%"],
                    hoverinfo="text",
                )
            )

    return fig


# Main function to generate the lesion size plot
def plot_longitudinal_lesions(df, template="light"):
    if template == "dark":
        template = constants.dark_theme
        lines_colors = ["#2a6a4f", "#8f2d56"]
        perc_diff_color = "#029ebf"
        annotation_colors = ["#a5e6ba", "#f2b5d4"]
    else:
        template = constants.light_theme
        lines_colors = ["#f4a261", "#e9c46a"]
        perc_diff_color = "#005f73"
        annotation_colors = ["#9c5c2a", "#8a6b1e"]

    # Step 1: Plot observed and predicted lesion sizes
    fig = plot_lines_with_markers(df, "time_point", ["lesion_size_whole", "lesion_size_pred"], lines_colors)

    # Step 2: Add percentage differences between observed and predicted sizes
    fig = add_percentage_differences(df, "time_point", ["lesion_size_whole", "lesion_size_pred"], fig, perc_diff_color)

    # Step 3: Add tumor growth annotations
    fig = add_tumor_growth_annotations(
        df, "time_point", ["lesion_size_whole", "lesion_size_pred"], fig, annotation_colors
    )

    # Finalize layout
    fig.update_layout(
        title="",
        template=template,
        height=600,
        width=1000,
        yaxis_title="Lesion Size (mm³)",
        xaxis_title="Timepoints",
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.55),
        hovermode="x unified",
    )
    fig.update_xaxes(tickmode="linear", dtick=1, tickformat=",d")
    return fig
