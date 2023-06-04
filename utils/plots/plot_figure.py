from plotly.graph_objs import Figure
from plotly.offline import plot


def plot_figure(figure: Figure) -> str:
    config = dict(
        displayModeBar=False,
    )
    return plot(figure, output_type="div", include_plotlyjs=False, config=config)
