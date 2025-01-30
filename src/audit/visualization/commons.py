from audit.app.util.commons.sidebars import setup_sidebar_plot_customization
from audit.app.util.commons.sidebars import setup_sidebar_matrix_customization


def update_plot_customization(fig, key=None):
    show_leg, leg_pos, leg_x, leg_y, leg_xanc, leg_yanc, xlabel, ylabel, title = setup_sidebar_plot_customization(key=key)

    if fig is not None:
        # Update the legend layout
        fig.update_layout(
            legend=dict(
                x=leg_x,
                y=leg_y,
                xanchor=leg_xanc,
                yanchor=leg_yanc,
            )
        )

        fig.update_layout(
            showlegend=show_leg,  # Show or hide the legend
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            title=dict(text=title, x=0.5),  # Center the title
        )

    return fig


def update_segmentation_matrix_plot(fig, classes, key="matrix"):
    x_axis_label, y_axis_label, class_labels = setup_sidebar_matrix_customization(classes, key=key)

    if fig is not None:
        fig.update_xaxes(
            tickvals=list(range(len(class_labels))),
            ticktext=class_labels,
            title_text=x_axis_label
        )

        fig.update_yaxes(
            tickvals=list(range(len(classes))),
            ticktext=class_labels,
            title_text=y_axis_label
        )

    return fig
