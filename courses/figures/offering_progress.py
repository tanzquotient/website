from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from plotly.graph_objs import Figure, Bar, Layout
from plotly.graph_objs.layout import Legend

from courses.models import Offering, OfferingType, Subscribe, MatchingState


def offering_progress() -> Figure:
    labels = []
    series_couple = []
    series_single = []
    series_unconfirmed = []

    for o in Offering.objects.filter(type=OfferingType.REGULAR).reverse().all():
        subscriptions = Subscribe.objects.filter(course__offering=o)
        labels.append(u'<a href="{}">{}</a>'.format(reverse('courses:offering_overview', args=[o.id]),
                                                    escape(o.name)))
        accepted = subscriptions.accepted()
        accepted_count = accepted.count()
        couple_count = accepted.filter(matching_state=MatchingState.COUPLE).count()
        single_count = accepted_count - couple_count
        unconfirmed_count = subscriptions.active().count() - accepted_count

        series_couple.append(couple_count)
        series_single.append(single_count)
        series_unconfirmed.append(unconfirmed_count)

    return Figure(
        data=[
            Bar(
                x=series_couple,
                y=labels,
                orientation='h',
                name=str(_("Couple subscriptions")),
                marker=dict(color='#C51718'),
            ),
            Bar(
                x=series_single,
                y=labels,
                orientation='h',
                name=str(_("Single subscriptions")),
                marker=dict(color='#DC7374'),
            ),
            Bar(
                x=series_unconfirmed,
                y=labels,
                orientation='h',
                name=str(_("Not confirmed")),
                marker=dict(color='#C8C8C8'),
            ),
        ],
        layout=Layout(
            height=len(labels)*25,
            margin=dict(l=0, r=0, t=0, b=0, pad=10),
            hovermode='y',
            barmode='stack',
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
            legend=Legend(x=0.5, y=1.02, orientation='h', yanchor='bottom', xanchor='center')
        )
    )