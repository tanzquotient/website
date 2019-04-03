from courses.utils import export_excel, export_csv, export_vcard


def export(export_format, *args, **kwargs):
    if export_format == 'xlsx':
        return export_excel(args, kwargs)
    elif export_format == 'vcard':
        return export_vcard(args, kwargs)
    elif export_format == 'csv' or export_format == 'google_csv':
        return export_csv(args, kwargs)
    else:
        return None
