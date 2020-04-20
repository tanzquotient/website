from __future__ import unicode_literals

import os
from io import open
from tempfile import gettempdir

from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


def generate_voucher_pdf(vouchers):
    basic_file = os.path.join(settings.BASE_DIR, 'payment', 'Voucher.svg')
    with open(basic_file, encoding='utf-8') as file:
        base_content = file.read()

    for voucher in vouchers:
        filename = "Voucher-" + voucher.key + ".pdf"

        if voucher.expires:
            date_string = ", Valid through: " + voucher.expires.strftime("%d.%m.%Y")
        else:
            date_string = ""

        content = base_content \
            .replace('{{ code }}', voucher.key) \
            .replace("{{ valid }}", date_string) \
            .replace("{{ percent }}", str(voucher.percentage))
        tmpdir = gettempdir()
        temp_path = os.path.join(tmpdir, 'voucher.svg')
        with open(temp_path, mode="wb") as temp_file:
            temp_file.write(content.encode('utf-8'))

        drawing = svg2rlg(temp_path)
        path = os.path.join(tmpdir, filename)
        renderPDF.drawToFile(drawing, path)
        with open(path, "r", encoding='latin1') as file:
            content = file.read()
        voucher.pdf_file.save(filename, ContentFile(content.encode('utf-8')))


# Admin action
def admin_action_generate_pdf(modeladmin, request, queryset):
    return generate_voucher_pdf(vouchers=queryset)


admin_action_generate_pdf.short_description = "Generate Voucher PDF"
