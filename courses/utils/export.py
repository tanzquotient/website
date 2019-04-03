from courses.utils import export_excel, export_csv, export_vcard


def export(export_format, title, data, multiple=False):
    if export_format in ['xlsx', 'excel']:
        return export_excel(title=title, multiple=multiple, data=data)
    elif export_format in ['vcf', 'vcard']:
        return export_vcard(data=data, multiple=multiple, title=title)
    elif export_format in ['csv', 'google_csv']:
        return export_csv(title=title, multiple=multiple, data=data)
    else:
        return None
