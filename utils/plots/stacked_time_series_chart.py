from datetime import date

from plotly.graph_objs import Bar, Figure, Layout
from plotly.graph_objs.layout import Legend, XAxis, YAxis

from . import DataSeries


def stacked_time_series_chart(dates: list[date], data: list[DataSeries]) -> Figure:
    return Figure(
        data=[
            Bar(
                x=dates,
                y=data_series.values,
                name=data_series.name,
                marker={"color": data_series.color} if data_series.color else None,
                visible=data_series.visible if data_series.visible else True,
            )
            for data_series in data
        ],
        layout=Layout(
            height=400,
            margin={"l": 0, "r": 0, "t": 0, "b": 0, "pad": 10},
            hovermode="x unified",
            barmode="stack",
            xaxis=XAxis(type="date", hoverformat="%a, %d.%m.%Y"),
            yaxis=YAxis(rangemode="tozero"),
            legend=Legend(
                x=0.5, y=1.02, orientation="h", yanchor="bottom", xanchor="center"
            ),
        ),
    )
