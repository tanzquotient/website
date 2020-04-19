from __future__ import unicode_literals

import os
import tempfile
from io import open

from django.conf import settings
from django.core.files.base import ContentFile

def generate_voucher_svg(vouchers):

    basic_file = os.path.join(settings.BASE_DIR, 'payment', 'Voucher.svg')
    with open(basic_file, encoding='utf-8') as file:
        content = file.read()

    for voucher in vouchers:
        filename = "Voucher-" + voucher.key + ".svg"

        if voucher.expires:
            date_string = "valid through " + voucher.expires.strftime("%m/%Y")
        else:
            date_string = ""

        file = ContentFile(content.replace('ABCDEF', voucher.key).replace("valid through 12/2017", date_string).encode('utf-8'))
        voucher.pdf_file.save(filename, file)


# Admin action
def admin_action_generate_svg(modeladmin, request, queryset):
    return generate_voucher_svg(vouchers=queryset)

admin_action_generate_svg.short_description = "Generate Voucher SVG"
