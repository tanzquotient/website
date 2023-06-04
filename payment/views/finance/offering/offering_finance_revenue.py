from _decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from courses.models import Offering
from utils import export


def get_data(offering:Offering):
    rows = [['Course','Wages']]
    for course in offering.course_set.all():
        hours = Decimal(course.get_total_time()['total']) if not course.cancelled else 0
        total = 0
        for teaching in course.teaching.all():
            total += teaching.hourly_wage * hours
        rows.append([course.name, total])
    return rows


@staff_member_required
def offering_finance_revenue(request: HttpRequest,offering_id:int) -> HttpResponse:
    offering = get_object_or_404(Offering,id = offering_id)

    export_format = request.GET.get('format', None)
    if export_format in ['excel', 'csv']:
        return export(export_format, title=_('Revenue overview'), data=get_data(offering))

    return render(request, 'finance/offering/revenue/index.html',
                  dict(title=_('Revenue overview'),active='revenue', url_key='payment:offering_revenue', data=get_data(offering),offering=offering))


