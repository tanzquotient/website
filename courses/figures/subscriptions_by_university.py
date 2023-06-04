from plotly.graph_objs import Figure

from courses.models import StudentStatus, Subscribe
from utils.plots import pie_chart


def subscriptions_by_university() -> Figure:
    return pie_chart(
        labels=[label for _, label in StudentStatus.CHOICES],
        values=[
            Subscribe.objects.active().filter(user__profile__student_status=key).count()
            for key, _ in StudentStatus.CHOICES
        ],
    )
