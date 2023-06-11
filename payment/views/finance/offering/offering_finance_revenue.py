from _decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from courses.models import Offering
from utils import export


def get_data(offering: Offering):
    header = [
        "Course",
        "Profit Margin",
        "Wages",
        "Fully booked legi Profit",
        "Profit",
        "Actual Profit",
        "Total Revenue after Reductions",
        "Actually paid",
        "Percent not paid",
    ]
    rows = [header]
    rows_total = [0] * len(header)
    rows_total[0] = "TOTAL"

    for course in offering.course_set.all():
        hours = (
            Decimal(course.get_total_time()["total"])
            if not (
                course.cancelled  # or course.get_confirmed_count == 0
                or course.is_external()
            )
            else 0
        )

        wages = sum(teaching.hourly_wage * hours for teaching in course.teaching.all())

        totals = course.payment_totals()
        paid = totals["paid"]
        to_pay_after_reductions = totals["to_pay_after_reductions"]

        max_revenue = (course.price_with_legi or 0) * (course.max_subscribers or 0)

        profit = to_pay_after_reductions - wages
        actual_profit = paid - wages

        # Calculate profit margin
        if to_pay_after_reductions != 0:
            profit_margin = (profit / to_pay_after_reductions) * 100
            percent_not_paid = (1 - (paid / to_pay_after_reductions)) * 100
        else:
            profit_margin = 0
            percent_not_paid = 0

        row = [
            course.name,
            profit_margin,
            wages,
            max_revenue - wages,
            profit,
            actual_profit,
            to_pay_after_reductions,
            paid,
            percent_not_paid,
        ]

        rows_total[1:] = [
            total + value for total, value in zip(rows_total[1:], row[1:])
        ]

        row = (
            [row[0]]
            + [f"{row[1]:.0f} %"]
            + [f"{value:.0f}" for value in row[2:-1]]
            + [f"{row[-1]:.0f} %"]
        )

        rows.append(row)

    total_profit = 100 * rows_total[4] / rows_total[6]
    total_percent_not_paid = 100 * (1 - (rows_total[7] / rows_total[6]))

    rows_total = (
        [rows_total[0]]
        + [f"{total_profit:.0f} %"]
        + [f"{value:.0f}" for value in rows_total[2:-1]]
        + [f"{total_percent_not_paid:.0f} %"]
    )
    rows.append(rows_total)
    return rows


@staff_member_required
def offering_finance_revenue(request: HttpRequest, offering_id: int) -> HttpResponse:
    offering = get_object_or_404(Offering, id=offering_id)

    export_format = request.GET.get("format", None)
    if export_format in ["excel", "csv"]:
        return export(
            export_format, title=_("Revenue overview"), data=get_data(offering)
        )

    return render(
        request,
        "finance/offering/revenue/index.html",
        dict(
            title=_("Revenue overview"),
            active="revenue",
            url_key="payment:offering_revenue",
            data=get_data(offering),
            offering=offering,
        ),
    )
