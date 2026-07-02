from django.http import HttpResponse

from .export_csv import export_csv
from .export_excel import export_excel
from .export_vcard import export_vcard


def export(export_format, title, data, multiple=False) -> HttpResponse:
    if export_format in ["xlsx", "excel"]:
        return export_excel(title=title, multiple=multiple, data=data)
    if export_format in ["vcf", "vcard"]:
        return export_vcard(data=data, multiple=multiple, title=title)
    if export_format in ["csv", "google_csv"]:
        return export_csv(title=title, multiple=multiple, data=data)
    raise ValueError(f"Unknown export format {export_format}")
