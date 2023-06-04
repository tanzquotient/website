from django import template
from django.contrib.auth.models import User

from courses.models import Offering, Teach

register = template.Library()


@register.inclusion_tag(filename="finance/offering/teachers/table.html")
def teachers_table(offering: Offering):
    from payment import services

    _, personal_data, courses = services.offering_finance_teachers([offering])
    return dict(personal_data=personal_data, courses=courses)
