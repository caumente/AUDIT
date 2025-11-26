import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


class Dashboard:
    def __init__(self):
        self.discrete_color_palette = px.colors.qualitative.Pastel
        self.continuous_color_palette = px.colors.sequential.Blues
        self.light_theme = "simple_white"
        custom_dark_theme = pio.templates["plotly_dark"]
        custom_dark_theme.layout.update(
            plot_bgcolor="#0e1117",  # Custom dark background
            paper_bgcolor="#0e1117",  # Custom border color
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                ticks="outside",
                ticklen=5,
                tickwidth=1,
                tickcolor="white",
                showline=True,
                linewidth=1,
                linecolor="white",
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                ticks="outside",
                ticklen=5,
                tickwidth=1,
                tickcolor="white",
                showline=True,
                linewidth=1,
                linecolor="white",
            ),
        )
        # Register and assign it to self.dark_theme
        pio.templates["custom_dark"] = custom_dark_theme
        self.dark_theme = "custom_dark"  # Now, self.dark_theme uses the modified template

        self.other_dark_theme = dict(
            layout=go.Layout(
                plot_bgcolor="#0e1117",  # dark background
                paper_bgcolor="#0e1117",  # border color
                font=dict(color="white"),  # white text
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    automargin=True,
                    ticks="outside",
                    ticklen=5,
                    tickwidth=1,
                    tickcolor="white",
                    showline=True,
                    linewidth=1,
                    linecolor="white",
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    automargin=True,
                    ticks="outside",
                    ticklen=5,
                    tickwidth=1,
                    tickcolor="white",
                    showline=True,
                    linewidth=1,
                    linecolor="white",
                ),
            )
        )

        self.bar_width = 0.8
