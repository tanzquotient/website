from django.urls import reverse
from django.utils.html import escape
from plotly.graph_objs import Figure

from courses.models import Offering, OfferingType, Subscribe, StudentStatus
from utils.plots import stacked_bar_chart, DataSeries


def offering_by_student_status() -> Figure:
    offerings = list(Offering.objects.filter(type=OfferingType.REGULAR).reverse().all())

    colors = {
        StudentStatus.ETH: '#073b4c',
        StudentStatus.UNI: '#118ab2',
        StudentStatus.PH: '#06d6a0',
        StudentStatus.OTHER: '#ffd166',
        StudentStatus.NO: '#ef476f',
    }

    return stacked_bar_chart(
        labels=[
            f'<a href="{reverse("courses:offering_overview", args=[o.id])}">{escape(o.name)}</a>' for o in offerings
        ],
        data=[
            DataSeries(
                name=label,
                values=[Subscribe.objects.filter(user__profile__student_status=key, course__offering=o).count()
                        for o in offerings],
                color=colors.get(key)
            ) for key, label in StudentStatus.CHOICES
        ])
