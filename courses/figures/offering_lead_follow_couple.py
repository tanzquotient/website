from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from plotly.graph_objs import Figure

from courses.models import Offering, Subscribe, MatchingState, LeadFollow
from utils.plots import stacked_bar_chart, DataSeries


def offering_lead_follow_couple(offering_type: str) -> Figure:
    offerings = list(Offering.objects.filter(type=offering_type).reverse().all())

    return stacked_bar_chart(
        labels=[
            f'<a href="{reverse("courses:offering_overview", args=[o.id])}">{escape(o.name)}</a>'
            for o in offerings
        ],
        data=[
            DataSeries(
                name=str(_("Couples")),
                values=[
                    Subscribe.objects.active()
                    .filter(
                        matching_state=MatchingState.COUPLE, course__offering=offering
                    )
                    .count()
                    for offering in offerings
                ],
                color="#936fac",
            ),
            DataSeries(
                name=str(_("Lead")),
                values=[
                    Subscribe.objects.active()
                    .filter(
                        course__offering=offering,
                        lead_follow=LeadFollow.LEAD,
                    )
                    .exclude(
                        matching_state__in=[
                            MatchingState.COUPLE,
                            MatchingState.NOT_REQUIRED,
                        ]
                    )
                    .count()
                    for offering in offerings
                ],
                color="#348aa7",
            ),
            DataSeries(
                name=str(_("No preference")),
                values=[
                    Subscribe.objects.active()
                    .filter(
                        course__offering=offering,
                        lead_follow=LeadFollow.NO_PREFERENCE,
                    )
                    .exclude(
                        matching_state__in=[
                            MatchingState.COUPLE,
                            MatchingState.NOT_REQUIRED,
                        ]
                    )
                    .count()
                    for offering in offerings
                ],
                color="#5dd39e",
            ),
            DataSeries(
                name=str(_("Follow")),
                values=[
                    Subscribe.objects.active()
                    .filter(
                        course__offering=offering,
                        lead_follow=LeadFollow.FOLLOW,
                    )
                    .exclude(
                        matching_state__in=[
                            MatchingState.COUPLE,
                            MatchingState.NOT_REQUIRED,
                        ]
                    )
                    .count()
                    for offering in offerings
                ],
                color="#bce784",
            ),
            DataSeries(
                name=str(_("Not required")),
                values=[
                    Subscribe.objects.active()
                    .filter(
                        matching_state=MatchingState.NOT_REQUIRED,
                        course__offering=offering,
                    )
                    .count()
                    for offering in offerings
                ],
                color="#9db4c0",
            ),
        ],
    )
