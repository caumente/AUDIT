import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go


def create_custom_cmap(theme="light"):
    """
    Create a custom colormap based on the selected theme.
    Args:
        theme (str): 'light' or 'dark' to specify the theme.
    Returns:
        list: Plotly color scale.
    """
    if theme == "dark":
        start_color = np.array([14, 17, 23]) / 255.0  # 0e1117
        end_color = np.array([140, 140, 140]) / 255.0
        cmap_colors = np.linspace(start_color, end_color, 100)
    else:
        # For light theme, use the 'Blues' colormap
        blue_colors = plt.cm.Blues(np.linspace(0.0, 0.5, 100))
        cmap_colors = blue_colors

    # Convert to RGB format for Plotly
    plotly_colorscale = [
        [i / 99, f"rgb({int(cmap_colors[i, 0] * 255)}, {int(cmap_colors[i, 1] * 255)}, {int(cmap_colors[i, 2] * 255)})"]
        for i in range(100)
    ]
    return plotly_colorscale


def add_grid_lines(fig, matrix_shape, theme="light"):
    """
    Add grid lines to the heatmap figure.
    Args:
        fig (go.Figure): The figure object.
        matrix_shape (tuple): Shape of the matrix (rows, cols).
        theme (str): 'light' or 'dark' for color of grid lines.
    """
    grid_color = "#dee2e6" if theme == "dark" else "black"

    nrows, ncols = matrix_shape
    shapes = []

    # Horizontal lines
    for i in range(1, nrows):
        shapes.append(
            dict(type="line", x0=-0.5, y0=i - 0.5, x1=ncols - 0.5, y1=i - 0.5, line=dict(color=grid_color, width=1))
        )

    # Vertical lines
    for j in range(1, ncols):
        shapes.append(
            dict(type="line", x0=j - 0.5, y0=-0.5, x1=j - 0.5, y1=nrows - 0.5, line=dict(color=grid_color, width=1))
        )

    # Outer border
    shapes.append(
        dict(type="rect", x0=-0.5, y0=-0.5, x1=ncols - 0.5, y1=nrows - 0.5, line=dict(color=grid_color, width=2))
    )

    fig.update_layout(shapes=shapes)


def create_annotations(matrix, classes, normalized=True, theme="light"):
    """
    Annotate the heatmap with values.
    Args:
        matrix (np.array): Confusion matrix.
        classes (list): List of class labels.
        normalized (bool): Whether to show percentages or absolute values.
        theme (str): 'light' or 'dark' for color of axis labels.
    Returns:
        list: List of annotations for the heatmap.
    """
    annotations = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i != j:
                text = f"{matrix[i, j]:.1f}%" if normalized else f"{matrix[i, j]:,}"
                annotations.append(
                    go.layout.Annotation(
                        text=text,
                        x=classes[j],
                        y=classes[i],
                        xref="x1",
                        yref="y1",
                        font=dict(color="black" if theme == "light" else "white", size=30),
                        showarrow=False,
                    )
                )
    return annotations


def update_axes(fig, classes, theme="light"):
    """
    Update the x and y axes for the heatmap.
    Args:
        fig (go.Figure): The figure object.
        classes (list): List of class labels.
        theme (str): 'light' or 'dark' for color of axis labels.
    """
    text_color = "black" if theme == "light" else "#dee2e6"

    fig.update_xaxes(
        tickangle=0,
        tickvals=list(range(len(classes))),
        ticktext=classes,
        title_text="Predicted label",
        title_font=dict(size=30, color=text_color),
        tickfont=dict(size=30, color=text_color),
        title_standoff=50,
        side="top",
    )

    fig.update_yaxes(
        tickangle=0,
        tickvals=list(range(len(classes))),
        ticktext=classes,
        title_text="True label",
        title_font=dict(size=30, color=text_color),
        tickfont=dict(size=30, color=text_color),
        title_standoff=50,
        autorange="reversed",
    )


def plt_confusion_matrix(matrix, classes, theme="light", normalized=True):
    """
    Plotly version of the confusion matrix visualization with custom colormap and grid lines.
    Args:
        matrix (np.array): Confusion matrix.
        classes (list): List of class labels.
        theme (str): 'light' or 'dark' for the theme.
        normalized (bool): Whether to normalize the matrix.
    Returns:
        go.Figure: Plotly figure object.
    """
    # Create custom color map based on the selected theme
    custom_cmap = create_custom_cmap(theme)

    # Create the heatmap figure
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=classes,
            y=classes,
            colorscale=custom_cmap,
            showscale=True,
            zmin=0,
            zmax=np.max(matrix),
            colorbar=dict(
                thickness=20,
                outlinecolor="black" if theme == "light" else "#dee2e6",
                outlinewidth=2,
                ticks="outside",
            ),
            hovertemplate="Predicted label: %{x}<br>"
            "True label: %{y}<br>"
            "Misclassified pixels</b>: %{z:.1f}<extra></extra>",
        )
    )

    # Add grid lines
    add_grid_lines(fig, matrix.shape, theme)

    # Annotate the matrix
    annotations = create_annotations(matrix, classes, normalized, theme)
    fig.update_layout(annotations=annotations)

    # Update axes labels
    update_axes(fig, classes, theme)

    # Set layout properties
    fig.update_layout(
        plot_bgcolor="white" if theme == "light" else "#0e1117",
        paper_bgcolor="white" if theme == "light" else "#0e1117",
        width=600,
        height=600,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=0, r=0, t=50, b=0),
    )

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
    custom_blues_cmap = create_custom_cmap("light")

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

    return fig


def plt_confusion_matrix_plotly_dark(matrix, classes, normalized=True):
    """
    Plotly version of the confusion matrix visualization adapted for dark theme.

    Args:
        matrix (np.array): Confusion matrix.
        classes (list): List of class labels.
        normalized (bool): Whether the confusion matrix is normalized.

    Returns:
        go.Figure: Plotly figure object.
    """

    def add_grid_lines_dark(fig, matrix_shape):
        nrows, ncols = matrix_shape
        shapes = []

        # Horizontal lines
        for i in range(1, nrows):
            shapes.append(
                dict(type="line", x0=-0.5, y0=i - 0.5, x1=ncols - 0.5, y1=i - 0.5, line=dict(color="#dee2e6", width=1))
            )

        # Vertical lines
        for j in range(1, ncols):
            shapes.append(
                dict(type="line", x0=j - 0.5, y0=-0.5, x1=j - 0.5, y1=nrows - 0.5, line=dict(color="#dee2e6", width=1))
            )

        # Outer border
        shapes.append(
            dict(type="rect", x0=-0.5, y0=-0.5, x1=ncols - 0.5, y1=nrows - 0.5, line=dict(color="#dee2e6", width=2))
        )

        fig.update_layout(shapes=shapes)

    # Create the custom color scale
    custom_dark_cmap = create_custom_cmap("dark")

    # Process matrix (removing empty classes if needed)
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
            colorscale=custom_dark_cmap,
            showscale=True,
            zmin=0,
            zmax=np.max(x),
            colorbar=dict(
                thickness=20,
                outlinecolor="#dee2e6",  # Gray border around the color bar
                outlinewidth=2,
                ticks="outside",
                tickfont=dict(color="#dee2e6"),
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
                        font=dict(color="white", size=30),  # White text for dark background
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
        title_font=dict(size=30, color="#dee2e6"),
        tickfont=dict(size=30, color="#dee2e6"),
        title_standoff=50,
        side="top",
    )

    fig.update_yaxes(
        tickangle=0,
        tickvals=list(range(len(classes))),
        ticktext=classes,
        title_text="True label",
        title_font=dict(size=30, color="white"),
        tickfont=dict(size=30, color="white"),
        title_standoff=50,
        autorange="reversed",
    )

    # Add grid lines to the figure
    add_grid_lines_dark(fig, x.shape)

    fig.update_layout(
        plot_bgcolor="#0e1117",  # Dark background
        paper_bgcolor="#0e1117",
        width=600,
        height=600,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig
