from io import BytesIO
from zipfile import ZipFile

from django.http import HttpResponse

from . import clean_filename


def export_zip(title, files):
    zipped_file = BytesIO()
    with ZipFile(zipped_file, "w") as folder:
        for name, file_bytes in files.items():
            folder.writestr(
                f"{clean_filename(title)}/{clean_filename(name)}", file_bytes
            )
    length = len(zipped_file.getvalue())
    zipped_file.seek(0)

    response = HttpResponse(zipped_file, content_type="application/zip")
    response["Content-Disposition"] = (
        f"attachment; filename={clean_filename(title)}.zip"
    )
    response["Content-Length"] = length
    return response
