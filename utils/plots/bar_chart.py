from typing import Any

from plotly.graph_objs import Figure, Bar, Layout


def bar_chart(values: list[Any], labels: list[str]) -> Figure:
    labels.reverse()
    values.reverse()
    values_sum = max(sum(values), 1)
    percent = ["({:2.1f} %)".format(100 * v / values_sum) for v in values]

    return Figure(
        data=[
            Bar(
                x=values,
                y=labels,
                text=percent,
                orientation='h',
            )
        ],
        layout=Layout(
            height=len(values)*30,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0,
                pad=10,
            ),
            hovermode='y',
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )
    )
