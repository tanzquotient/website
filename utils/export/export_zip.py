from io import BytesIO
from zipfile import ZipFile

from django.http import HttpResponse

from . import clean_filename


def export_zip(title, files):
    zipped_file = BytesIO()
    with ZipFile(zipped_file, "w") as folder:
        for name, file_bytes in files.items():
            folder.writestr(
                "{}/{}".format(clean_filename(title), clean_filename(name)), file_bytes
            )
    length = len(zipped_file.getvalue())
    zipped_file.seek(0)

    response = HttpResponse(zipped_file, content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename={}.zip".format(
        clean_filename(title)
    )
    response["Content-Length"] = length
    return response
