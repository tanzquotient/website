from django.http import HttpResponse
from openpyxl import Workbook

from courses.utils import clean_filename


def export_excel(title, data, has_column_headings=True, multiple_sheets=False):

    workbook = Workbook()

    if multiple_sheets:
        sheets = dict()
        workbook.remove_sheet(workbook.get_active_sheet())
        for key, value in data:
            sheet_title = clean_filename(key)[:30]
            sheets[workbook.create_sheet(title=sheet_title)] = value
    else:
        sheets = {workbook.get_active_sheet(): data}

    for sheet, values in sheets:
        for row_number, row in enumerate(data):
            for col_number, value in enumerate(row):
                cell = sheet.cell(row=row_number + 1, column=col_number + 1, value=value)
                if has_column_headings and row_number == 0:
                    font = cell.font.copy()
                    font.bold = True
                    cell.font = font

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(clean_filename(title))

    workbook.save(response)
    return response
