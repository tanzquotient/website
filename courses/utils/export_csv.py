from io import BytesIO

import unicodecsv
from django.http import HttpResponse

from courses.utils import export_zip


def write_csv(data, file):
    writer = unicodecsv.writer(file)
    for row in data:
        writer.writerow(row)


def export_csv(title, data, multiple=False):

    if multiple:
        files = dict()
        for name, value in data.items():
            file = BytesIO()
            write_csv(value, file)
            files[name] = file.getvalue()

        return export_zip(title, files)

    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(title)
        write_csv(data, response)
        return response

