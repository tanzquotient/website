from typing import Any

from plotly.graph_objs import Bar, Figure, Layout


def bar_chart(values: list[Any], labels: list[str]) -> Figure:
    labels.reverse()
    values.reverse()
    values_sum = max(sum(values), 1)
    percent = [f"({100 * v / values_sum:2.1f} %)" for v in values]

    return Figure(
        data=[
            Bar(
                x=values,
                y=labels,
                text=percent,
                orientation="h",
            )
        ],
        layout=Layout(
            height=len(values) * 30,
            margin={
                "l": 0,
                "r": 0,
                "t": 0,
                "b": 0,
                "pad": 10,
            },
            hovermode="y",
            dragmode=False,
            xaxis={"fixedrange": True},
            yaxis={"fixedrange": True},
        ),
    )
