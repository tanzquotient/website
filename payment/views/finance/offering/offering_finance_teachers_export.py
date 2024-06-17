from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse

from courses.models import Offering
from utils import export


@staff_member_required
def offering_finance_teachers_export(
    request: HttpRequest, offering: int
) -> HttpResponse:
    export_format = request.GET.get("format", "csv")
    from payment import services

    export_name, data = services.offering_finance_teachers(
        Offering.objects.filter(id=offering).all()
    )
    return export(
        export_format,
        title=export_name,
        multiple=True,
        data=data,
    )
