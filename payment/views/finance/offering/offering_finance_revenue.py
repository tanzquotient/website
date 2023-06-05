from _decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from courses.models import Offering
from utils import export


def get_data(offering:Offering):
    rows = [['Course','Wages','Max legi revenue', 'total revenue after reductions', 'actually paid',
             'profit','actual profit']]
    for course in offering.course_set.all():
        hours = Decimal(course.get_total_time()['total']) if not course.cancelled else 0

        wages = 0
        for teaching in course.teaching.all():
            wages += teaching.hourly_wage * hours

        totals = course.payment_totals()
        try:
            max_revenue = course.price_with_legi * course.max_subscribers
        except:
            max_revenue = 0

        rows.append([course.name, wages, max_revenue,
                     totals['to_pay_after_reductions'], totals['paid'],totals['to_pay_after_reductions']-wages,
                     totals['paid']-wages])
    return rows


@staff_member_required
def offering_finance_revenue(request: HttpRequest,offering_id:int) -> HttpResponse:
    offering = get_object_or_404(Offering,id = offering_id)

    export_format = request.GET.get('format', None)
    if export_format in ['excel', 'csv']:
        return export(export_format, title=_('Revenue overview'), data=get_data(offering))

    return render(request, 'finance/offering/revenue/index.html',
                  dict(title=_('Revenue overview'),active='revenue', url_key='payment:offering_revenue', data=get_data(offering),offering=offering))


