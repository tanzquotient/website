from plotly.graph_objs import Figure, Bar, Layout
from plotly.graph_objs.layout import Legend, XAxis, YAxis, Hoverlabel

from . import DataSeries


def stacked_bar_chart(labels: list[str], data: list[DataSeries]) -> Figure:
    sum_by_label = {label: sum([data_series.values[idx] or 0 for data_series in data])
                    for idx, label in enumerate(labels)}
    return Figure(
        data=[
            Bar(
                x=[value if value else None for value in data_series.values],
                y=labels,
                text=[f"{value * 100 / sum_by_label[label]:.1f} %" if value and sum_by_label[label] != 0 else None
                      for label, value in zip(labels, data_series.values)],
                orientation='h',
                name=data_series.name,
                marker=dict(color=data_series.color) if data_series.color else None,
            ) for index, data_series in enumerate(data)
        ],
        layout=Layout(
            height=len(labels)*25,
            margin=dict(l=0, r=0, t=0, b=0, pad=10),
            hovermode='y',
            barmode='stack',
            dragmode=False,
            xaxis=XAxis(fixedrange=True),
            yaxis=YAxis(fixedrange=True),
            legend=Legend(x=0.5, y=1.02, orientation='h', yanchor='bottom', xanchor='center')
        )
    )
