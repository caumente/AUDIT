import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from matplotlib.colors import LinearSegmentedColormap


def plt_confusion_matrix(matrix, classes, normalized=True):

    # create a personalized Blues cmap
    blue_colors = plt.cm.Blues(np.linspace(0.0, 0.5, 100))
    custom_cmap = LinearSegmentedColormap.from_list("CustomBlues", blue_colors)

    classes_to_remove = []
    x = matrix.copy()
    if len(classes_to_remove) > 0:
        for c in classes_to_remove:
            classes.pop(c)
            x = np.delete(x, c, axis=0)
            x = np.delete(x, c, axis=1)

    # Plotting the normalized matrix as a heatmap with single color background and lines between rows
    fig, ax = plt.subplots(facecolor="w", edgecolor="k")  # Set the background color here
    ax.imshow(x, cmap=custom_cmap, vmin=0, vmax=np.max(x))

    # Adding annotations
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if i != j:
                if normalized:
                    plt.text(j, i, f"{x[i, j]:.1f}%", ha="center", va="center", color="black", fontsize=12)
                else:
                    plt.text(j, i, f"{x[i, j]:,}", ha="center", va="center", color="black", fontsize=12)

    # Adding gridlines between rows
    ax.set_xticks(np.arange(-0.5, x.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, x.shape[0], 1), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=1)

    # Adjusting ticks and gridlines
    plt.xticks(np.arange(x.shape[1]), labels=classes)
    plt.yticks(np.arange(x.shape[0]), labels=classes)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    plt.ylabel("True \nlabel", rotation=0, fontsize=12, labelpad=60)
    plt.suptitle("Predicted label", fontsize=12)

    # remove ticks
    plt.tick_params(axis="x", length=0)
    plt.tick_params(axis="y", length=0)
    plt.grid(False)

    # plt.title('Normalized Confusion Matrix')
    return fig


def plt_confusion_matrix_plotly(matrix, classes, normalized=True):
    """
    Plotly version of the confusion matrix visualization with custom blue colormap and black grid lines.

    Args:
        matrix (np.array): Confusion matrix.
        classes (list): List of class labels.
        normalized (bool): Whether the confusion matrix is normalized.

    Returns:
        go.Figure: Plotly figure object.
    """

    def create_custom_blues_cmap():
        # Generate the color values from 0.0 to 0.5 in the Blues colormap
        blue_colors = plt.cm.Blues(np.linspace(0.0, 0.5, 100))

        # Convert the colors to a format that Plotly accepts (RGB strings)
        plotly_colorscale = [
            [i / (len(blue_colors) - 1), f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"]
            for i, (r, g, b, _) in enumerate(blue_colors)
        ]

        return plotly_colorscale

    def add_grid_lines(fig, matrix_shape):
        nrows, ncols = matrix_shape
        shapes = []

        # Horizontal lines
        for i in range(1, nrows):
            shapes.append(
                dict(type="line", x0=-0.5, y0=i - 0.5, x1=ncols - 0.5, y1=i - 0.5, line=dict(color="black", width=1))
            )

        # Vertical lines
        for j in range(1, ncols):
            shapes.append(
                dict(type="line", x0=j - 0.5, y0=-0.5, x1=j - 0.5, y1=nrows - 0.5, line=dict(color="black", width=1))
            )

        # Outer border
        shapes.append(
            dict(type="rect", x0=-0.5, y0=-0.5, x1=ncols - 0.5, y1=nrows - 0.5, line=dict(color="black", width=2))
        )

        fig.update_layout(shapes=shapes)

    # Create the custom color scale
    custom_blues_cmap = create_custom_blues_cmap()

    classes_to_remove = []
    x = matrix.copy()
    if len(classes_to_remove) > 0:
        for c in classes_to_remove:
            classes.pop(c)
            x = np.delete(x, c, axis=0)
            x = np.delete(x, c, axis=1)

    # Create the heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=x,
            x=classes,
            y=classes,
            colorscale=custom_blues_cmap,
            showscale=True,
            zmin=0,
            zmax=np.max(x),
            colorbar=dict(
                thickness=20,
                outlinecolor="black",  # Black border around the color bar
                outlinewidth=2,
                ticks="outside",
            ),
            hovertemplate="Predicted label: %{x}<br>"
            "True label: %{y}<br>"
            "Misclassified pixels</b>: %{z:.1f}<extra></extra>",
        )
    )

    # Annotate the heatmap with text
    annotations = []
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if i != j:
                text = f"{x[i, j]:.1f}%" if normalized else f"{x[i, j]:,}"
                annotations.append(
                    go.layout.Annotation(
                        text=text,
                        x=classes[j],
                        y=classes[i],
                        xref="x1",
                        yref="y1",
                        font=dict(color="black", size=30),
                        showarrow=False,
                    )
                )
    fig.update_layout(annotations=annotations)

    # Set x and y axis labels
    fig.update_xaxes(
        tickangle=0,
        tickvals=list(range(len(classes))),
        ticktext=classes,
        title_text="Predicted label",
        title_font=dict(size=30, color="Black"),
        tickfont=dict(size=30, color="Black"),
        title_standoff=50,
        side="top",
        # scaleanchor="y",  # Ensures that x and y axes have the same scale
        # scaleratio=1      # Ensures that the aspect ratio is 1:1
    )

    fig.update_yaxes(
        tickangle=0,
        tickvals=list(range(len(classes))),
        ticktext=classes,
        title_text="True label",
        title_font=dict(size=30, color="Black"),
        tickfont=dict(size=30, color="Black"),
        title_standoff=50,
        autorange="reversed",
        # scaleanchor="x",  # Ensures that x and y axes have the same scale
        # scaleratio=1      # Ensures that the aspect ratio is 1:1
    )

    # Add grid lines to the figure
    add_grid_lines(fig, x.shape)

    fig.update_layout(
        plot_bgcolor="white",
        width=600,
        height=600,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),  # Rotate y-axis labels for readability
        margin=dict(l=0, r=0, t=50, b=0),  # Reduce margins to bring elements closer
    )

    # # Add a rotated label using annotations
    # fig.add_annotation(
    #     text="True label",
    #     x=-0.1,  # Adjust x position as needed
    #     y=0.5,  # Adjust y position as needed
    #     xref="paper",
    #     yref="paper",
    #     showarrow=False,
    #     font=dict(size=16, color="black"),
    #     textangle=-90  # Rotate the label
    # )

    return fig
