from typing import Any

from plotly.graph_objs import Figure, Pie, Layout


def pie_chart(values: list[Any], labels: list[Any]) -> Figure:
    labels.reverse()
    values.reverse()

    return Figure(
        data=[
            Pie(
                values=values,
                labels=labels,
            )
        ],
        layout=Layout(
            height=300,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0,
                pad=10,
            ),
            hovermode='y',
            dragmode=False,
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )
    )
