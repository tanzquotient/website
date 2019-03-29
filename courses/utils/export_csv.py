import unicodecsv
from io import BytesIO
from zipfile import ZipFile

from django.http import HttpResponse

from courses.utils import clean_filename


def export_csv(title, data, multiple_sheets=False):

    if multiple_sheets:
        zipped_file = BytesIO()
        with ZipFile(zipped_file, 'w') as folder:
            for sheet, value in data:
                csv_file = BytesIO()
                writer = unicodecsv.writer(csv_file, encoding='utf-8')
                for row in value:
                    writer.writerow(row)

                folder.writestr(u'{}/{}.csv'.format(clean_filename(title), clean_filename(sheet)), csv_file.getvalue())
                csv_file.seek(0)
        zipped_file.seek(0)

        response = HttpResponse(zipped_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(clean_filename(title))
        response['Content-Length'] = zipped_file.tell()
        return response

    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(title)
        writer = unicodecsv.writer(response)
        for row in data:
            writer.writerow(row)

        return response

