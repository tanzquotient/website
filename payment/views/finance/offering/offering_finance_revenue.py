from _decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from courses.models import Offering
from utils import export


def get_data(offering: Offering):
    header = ['Course', 'Wages', 'Fully booked legi revenue', 'Total revenue after reductions', 'Actually paid',
              'Profit', 'Actual profit']
    rows = [header]
    rows_total = [0] * len(header)
    rows_total[0] = 'Total'

    for course in offering.course_set.all():
        hours = Decimal(course.get_total_time()['total']) if not (course.cancelled #or course.get_confirmed_count == 0
                                                                  or course.is_external()) else 0

        wages = sum(teaching.hourly_wage * hours for teaching in course.teaching.all())

        totals = course.payment_totals()

        try:
            max_revenue = course.price_with_legi * course.max_subscribers
        except:
            max_revenue = 0

        row = [course.name, wages, max_revenue, totals['to_pay_after_reductions'], totals['paid'],
               totals['to_pay_after_reductions'] - wages, totals['paid'] - wages]

        rows_total[1:] = [total + value for total, value in zip(rows_total[1:], row[1:])]
        rows.append(row)

    rows.append(rows_total)
    return rows









@staff_member_required
def offering_finance_revenue(request: HttpRequest, offering_id:int) -> HttpResponse:
    offering = get_object_or_404(Offering, id = offering_id)

    export_format = request.GET.get('format', None)
    if export_format in ['excel', 'csv']:
        return export(export_format, title=_('Revenue overview'), data=get_data(offering))

    return render(request, 'finance/offering/revenue/index.html',
                  dict(title=_('Revenue overview'),active='revenue', url_key='payment:offering_revenue',
                       data=get_data(offering),offering=offering))


