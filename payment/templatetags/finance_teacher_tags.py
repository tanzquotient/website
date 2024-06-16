from django import template

from courses.models import Offering

register = template.Library()


@register.inclusion_tag(filename="finance/offering/teachers/table.html")
def teachers_table(offering: Offering):
    from payment import services

    _, personal_data, teachings, courses = services.offering_finance_teachers(
        [offering], use_html=True
    )
    return dict(personal_data=personal_data, teachings=teachings, courses=courses)
