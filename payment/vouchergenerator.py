from __future__ import unicode_literals

import os
from io import open

from PyPDF2 import PdfFileWriter, PdfFileReader
from django.conf import settings
from django.http import FileResponse


def generate_pdf(modeladmin, request, queryset):

    basic_file = os.path.join(settings.BASE_DIR,'payment', 'Voucher.svg')
    with open(basic_file, encoding='utf-8') as f:
        content = f.read()

    for voucher in queryset:
        filename = "Voucher-" + voucher.key + ".svg"
        path = os.path.join(settings.MEDIA_ROOT, filename)

        if voucher.expires:
            date_string = "valid through " + voucher.expires.strftime("%m/%Y")
        else:
            date_string = ""

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.replace('ABCDEF', voucher.key).replace("valid through 12/2017", date_string))

        voucher.pdf_file.name = filename
        voucher.save()

generate_pdf.short_description = "Generate Voucher PDF"

# Creating a routine that appends files to the output file
def append_pdf(input, output):
    [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]


def join_pdfs(modeladmin, request, queryset):
    # first ensure pdfs are created for all vouchers in queryset
    generate_pdf(modeladmin, request, queryset)

    # Creating an object where pdf pages are appended to
    output = PdfFileWriter()
    # Appending two pdf-pages from two different files
    for voucher in queryset:
        append_pdf(PdfFileReader(open(os.path.join(settings.MEDIA_ROOT, voucher.pdf_file.name),"rb")),output)

    # Writing all the collected pages to a file
    first_voucher_key = queryset.first().key
    last_voucher_key = queryset.last().key
    filename = "Vouchers-" + first_voucher_key + "-" + last_voucher_key + ".pdf"
    with open(os.path.join(settings.MEDIA_ROOT, filename),"wb") as f:
        output.write(f)

    return FileResponse(open(os.path.join(settings.MEDIA_ROOT, filename), 'rb'), content_type='application/pdf')
join_pdfs.short_description = "Download Joined PDF"
