from audit.app.util.constants.sidebars import setup_sidebar_longitudinal_plot
from audit.app.util.constants.sidebars import setup_sidebar_matrix_customization
from audit.app.util.constants.sidebars import setup_sidebar_multimodel_plot
from audit.app.util.constants.sidebars import setup_sidebar_plot_customization


def update_plot_customization(fig, key=None):
    (
        show_leg,
        leg_pos,
        leg_x,
        leg_y,
        leg_xanc,
        leg_yanc,
        xlabel,
        ylabel,
        title,
        font_size,
    ) = setup_sidebar_plot_customization(key=key)

    if fig is not None:
        # Update the legend layout
        fig.update_layout(
            showlegend=show_leg,
            legend=dict(
                x=leg_x,
                y=leg_y,
                xanchor=leg_xanc,
                yanchor=leg_yanc,
            ),
        )
        # title
        fig.update_layout(title=dict(text=title, x=0.5), title_font=dict(size=font_size))
        # axes
        fig.for_each_xaxis(lambda x: x.update(title_text=xlabel))
        fig.for_each_yaxis(lambda y: y.update(title_text=ylabel))
        fig.update_layout(
            xaxis=dict(
                title_font=dict(size=font_size),  # Increase x-axis title font size
                tickfont=dict(size=font_size),  # Increase x-axis tick font size
            ),
            yaxis=dict(
                title_font=dict(size=font_size),  # Increase y-axis title font size
                tickfont=dict(size=font_size),  # Increase y-axis tick font size
            ),
            legend=dict(font=dict(size=font_size)),  # Increase legend font size
        )
        # annotations
        fig.update_layout(
            annotations=[
                dict(
                    font=dict(size=font_size),
                )
                for anno in fig.layout.annotations
            ]
        )
    return fig


def update_segmentation_matrix_plot(fig, classes, key="matrix"):
    x_axis_label, y_axis_label, class_labels = setup_sidebar_matrix_customization(classes, key=key)

    if fig is not None:
        fig.update_xaxes(tickvals=list(range(len(class_labels))), ticktext=class_labels, title_text=x_axis_label)

        fig.update_yaxes(tickvals=list(range(len(classes))), ticktext=class_labels, title_text=y_axis_label)

    return fig


def update_multimodel_plot(fig, classes, key=None):
    (
        show_leg,
        legend_position,
        leg_x,
        leg_y,
        leg_xanc,
        leg_yanc,
        class_labels,
        plot_title,
        font_size,
        ylabel,
        xlabel,
    ) = setup_sidebar_multimodel_plot(classes, key=key)

    if fig is not None:
        # Update the legend layout
        fig.update_layout(
            showlegend=show_leg,
            legend=dict(
                x=leg_x,
                y=leg_y,
                xanchor=leg_xanc,
                yanchor=leg_yanc,
            ),
        )

        # title
        fig.update_layout(title=dict(text=plot_title, x=0.5), title_font=dict(size=font_size))

        for idx, annotation in enumerate(fig.layout.annotations):
            if idx < len(class_labels):
                annotation.update(text=class_labels[idx], font=dict(size=font_size))

        fig.for_each_xaxis(lambda x: x.update(title_text=xlabel))
        fig.for_each_yaxis(lambda y: y.update(title_text=ylabel))

    return fig


def update_longitudinal_plot(fig, key=None):
    show_leg, plot_title, font_size, ylabel, xlabel = setup_sidebar_longitudinal_plot(key=key)

    if fig is not None:
        # Update the legend layout
        fig.update_layout(showlegend=show_leg)

        # title
        fig.update_layout(title=dict(text=plot_title, x=0.5), title_font=dict(size=font_size))

        fig.for_each_xaxis(lambda x: x.update(title_text=xlabel))
        fig.for_each_yaxis(lambda y: y.update(title_text=ylabel))

        fig.update_layout(
            xaxis=dict(
                title_font=dict(size=font_size),  # Increase x-axis title font size
                tickfont=dict(size=font_size),  # Increase x-axis tick font size
            ),
            yaxis=dict(
                title_font=dict(size=font_size),  # Increase y-axis title font size
                tickfont=dict(size=font_size),  # Increase y-axis tick font size
            ),
            legend=dict(font=dict(size=font_size)),  # Increase legend font size
        )
        # annotations
        fig.update_layout(
            annotations=[
                dict(
                    font=dict(size=font_size),
                )
                for anno in fig.layout.annotations
            ]
        )

    return fig
