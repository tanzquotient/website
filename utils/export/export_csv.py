import csv
from io import StringIO

from django.http import HttpResponse

from . import export_zip, clean_filename


def write_csv(data, file):
    writer = csv.writer(file)
    for row in data:
        writer.writerow(row)


def export_csv(title, data, multiple=False):
    if multiple:
        files = dict()
        for count, item in enumerate(data):
            file = StringIO()
            write_csv(item["data"], file)
            files["{}_{}.csv".format(count + 1, item["name"])] = file.getvalue().encode(
                "utf-8"
            )

        return export_zip(title, files)

    else:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(
            clean_filename(title)
        )
        write_csv(data, response)
        return response
