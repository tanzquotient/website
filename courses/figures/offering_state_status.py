from django.urls import reverse
from django.utils.html import escape
from plotly.graph_objs import Figure

from courses.models import Offering, Subscribe, SubscribeState
from utils.plots import stacked_bar_chart, DataSeries


def offering_state_status(offering_type: str) -> Figure:
    offerings = list(Offering.objects.filter(type=offering_type).reverse().all())

    colors = {
        SubscribeState.NEW: '#936fac',
        SubscribeState.CONFIRMED: '#f29222',
        SubscribeState.COMPLETED: '#0cb2af',
        SubscribeState.PAID: '#a1c65d',
        SubscribeState.REJECTED: '#e95e50',
        SubscribeState.TO_REIMBURSE: '#fac723',
    }

    return stacked_bar_chart(
        labels=[
            f'<a href="{reverse("courses:offering_overview", args=[o.id])}">{escape(o.name)}</a>' for o in offerings
        ],
        data=[
            DataSeries(
                name=label,
                values=[Subscribe.objects.filter(state=key, course__offering=o).count() for o in offerings],
                color=colors.get(key)
            ) for key, label in SubscribeState.CHOICES
        ])
