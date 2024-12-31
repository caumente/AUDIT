import plotly.express as px


class Dashboard:
    def __init__(self):

        self.discrete_color_palette = px.colors.qualitative.Pastel
        self.continuous_color_palette = px.colors.sequential.Blues
        self.template = "simple_white"

        self.bar_width = 0.8
