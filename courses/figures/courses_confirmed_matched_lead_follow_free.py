from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from plotly.graph_objs import Figure

from courses.models import Offering, Subscribe, MatchingState, LeadFollow
from utils.plots import stacked_bar_chart, DataSeries


def courses_confirmed_matched_lead_follow_free(offering: Offering) -> Figure:
    courses = list(offering.course_set.order_by('-name').all())

    return stacked_bar_chart(
        labels=[f"<span id='{course.id}'>{course.name}</span>" for course in courses],
        data=[
            DataSeries(
                name=str(_('Confirmed')),
                values=[course.subscriptions.accepted().count() for course in courses],
                color='#073b4c',
            ),
            DataSeries(
                name=str(_('Matched')),
                values=[course.subscriptions.new().matched().count() for course in courses],
                color='#936fac',
            ),
            DataSeries(
                name=str(_('Lead')),
                values=[course.subscriptions.new().single_with_preference(LeadFollow.LEAD).count() for course in courses],
                color='#348aa7'
            ),
            DataSeries(
                name=str(_('No preference')),
                values=[course.subscriptions.new().single_with_preference(LeadFollow.NO_PREFERENCE).count()
                        for course in courses],
                color='#5dd39e',
            ),
            DataSeries(
                name=str(_('Follow')),
                values=[course.subscriptions.new().single_with_preference(LeadFollow.FOLLOW).count() for course in courses],
                color='#bce784',
            ),
            DataSeries(
                name=str(_('Free')),
                values=[max(0, course.max_subscribers - course.subscriptions.active().count())
                        if course.max_subscribers else None for course in courses],
                color='#9db4c0',
            ),
        ])
