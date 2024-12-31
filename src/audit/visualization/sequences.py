import plotly.express as px


def plot_seq(seq, seq_name=None, slice=1):
    fig = px.imshow(seq[slice, :, :], binary_string=True, title=seq_name)
    fig.update_traces(hovertemplate="x: %{x} <br>y: %{y} <br>Pixel Intensity: %{z[0]}<extra></extra>")
    fig.update_layout(height=300, width=300, showlegend=False, margin=dict(b=30, t=30))

    return fig
