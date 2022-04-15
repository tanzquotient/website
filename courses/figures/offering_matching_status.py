from django.urls import reverse
from django.utils.html import escape
from plotly.graph_objs import Figure

from courses.models import Offering, Subscribe, MatchingState
from utils.plots import stacked_bar_chart, DataSeries


def offering_matching_status(offering_type: str) -> Figure:
    offerings = list(Offering.objects.filter(type=offering_type).reverse().all())

    colors = {
        MatchingState.COUPLE: '#936fac',
        MatchingState.MATCHED: '#a1c65d',
        MatchingState.NOT_REQUIRED: '#0cb2af',
        MatchingState.TO_MATCH: '#f29222',
        MatchingState.TO_REMATCH: '#e95e50',
        MatchingState.UNKNOWN: '#fac723',
    }

    return stacked_bar_chart(
        labels=[
            f'<a href="{reverse("courses:offering_overview", args=[o.id])}">{escape(o.name)}</a>' for o in offerings
        ],
        data=[
            DataSeries(
                name=label,
                values=[Subscribe.objects.active().filter(matching_state=key, course__offering=o).count()
                        for o in offerings],
                color=colors.get(key)
            ) for key, label in MatchingState.CHOICES
        ])
