from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from utils import export


def table_view_or_export(
    request: HttpRequest, title: str, url_key: str, data: list, template: str = None
) -> HttpResponse:
    export_format = request.GET.get("format", None)
    if export_format in ["excel", "csv"]:
        return export(export_format, title=title, data=data)

    return render(
        request,
        template or "snippets/table_view_and_export.html",
        dict(title=title, url_key=url_key, data=data),
    )
